"""
YPENG oscilloscope data analysis (CSV data attained from Rigol DS1054Z)

CSV files contain time and voltage samples (waveform)

Turn raw waveform CSV(s) → a small table of metrics + plots + repeatability statistics.

Calculate Peak-to-Peak Voltage (Vpp) for each waveform:
- Vpp = max(v) − min(v)

Calculate Repeatability Metrics:
- Mean Vpp across all waveforms
- Standard Deviation of Vpp across all waveforms
- Coefficient of Variation (CV) = (Standard Deviation / Mean) × 100

Create Plots - start with 3:
1) Waveform Plot: Time vs Voltage 
2) Vpp vs tap number - shows drift, fatigue, inconsistent tapping, outliers
3) Histogram of Vpp values - shows spread and repeatability visually
"""

import os
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# -----------------------------
# Rigol CSV parsing (Start/Increment format)
# -----------------------------
def read_rigol_csv(path: str):
    """
    Reads Rigol waveform CSV where time is encoded as:
        time = Start + Increment * index

    Expected header pattern:
      X,CH1,Start,Increment,
      Sequence,Volt,<Start>,<Increment>
      0,<v0>,
      1,<v1>,
      ...
    Returns:
      t (np.ndarray): time in seconds
      v (np.ndarray): voltage in volts
      start (float), inc (float)
    """
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    if len(lines) < 3:
        raise ValueError("CSV too short (not a Rigol waveform export?).")

    meta = [x.strip() for x in lines[1].split(",") if x.strip() != ""]
    # meta should be: ["Sequence","Volt","<Start>","<Increment>"]
    if len(meta) < 4:
        raise ValueError("Could not parse Start/Increment from the second line.")

    start = float(meta[2])
    inc = float(meta[3])

    idx_list = []
    v_list = []

    for line in lines[2:]:
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 2:
            continue
        try:
            idx = int(parts[0])
            volt = float(parts[1])
            idx_list.append(idx)
            v_list.append(volt)
        except ValueError:
            # Skip non-numeric junk lines safely
            continue

    if not idx_list:
        raise ValueError("No numeric waveform rows found.")

    idx = np.array(idx_list, dtype=int)
    v = np.array(v_list, dtype=float)
    t = start + inc * idx
    return t, v, start, inc


# -----------------------------
# Tap detection + Vpp extraction
# -----------------------------
def detect_taps_and_vpp(t, v, threshold_v=0.02, min_gap_s=0.15, pre_s=0.02, post_s=0.08):
    """
    Detects taps in a long waveform and computes per-tap Vpp.

    Logic:
    - Look at abs(v) so positive/negative spikes both count
    - Find samples where abs(v) >= threshold
    - Group them into events separated by >= min_gap_s
    - For each event, compute Vpp in [event_time - pre_s, event_time + post_s]

    Returns:
      events: list of dicts with keys: time_center, i_center, vpp, i0, i1
    """
    abs_v = np.abs(v)
    above = abs_v >= threshold_v
    if not np.any(above):
        return []

    # Convert min_gap from seconds -> samples (using median dt)
    dt = float(np.median(np.diff(t)))
    min_gap_n = max(1, int(min_gap_s / dt))

    # Find indices where above-threshold
    idxs = np.where(above)[0]

    # Group into events by gaps
    events = []
    start_i = idxs[0]
    prev_i = idxs[0]

    for i in idxs[1:]:
        if (i - prev_i) > min_gap_n:
            # close previous event
            end_i = prev_i
            events.append((start_i, end_i))
            start_i = i
        prev_i = i
    events.append((start_i, prev_i))

    # For each event, pick a center index = max abs(v) within the event window
    out = []
    for (a, b) in events:
        seg = abs_v[a:b+1]
        local_peak = int(a + np.argmax(seg))
        t0 = t[local_peak] - pre_s
        t1 = t[local_peak] + post_s

        # window indices
        i0 = int(np.searchsorted(t, t0, side="left"))
        i1 = int(np.searchsorted(t, t1, side="right")) - 1
        i0 = max(0, i0)
        i1 = min(len(t) - 1, i1)

        vw = v[i0:i1+1]
        vpp = float(np.max(vw) - np.min(vw))

        out.append({
            "time_center": float(t[local_peak]),
            "i_center": int(local_peak),
            "i0": int(i0),
            "i1": int(i1),
            "vpp": vpp
        })

    return out


# -----------------------------
# Tkinter App with tabs
# -----------------------------
class RigolAnalyzerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Rigol Tap Analyzer (Many taps in one CSV)")
        self.geometry("1100x750")

        # Data
        self.filepath = None
        self.t = None
        self.v = None
        self.events = []

        # Controls frame
        ctrl = ttk.Frame(self)
        ctrl.pack(side=tk.TOP, fill=tk.X, padx=10, pady=8)

        ttk.Button(ctrl, text="Open Rigol CSV…", command=self.open_file).pack(side=tk.LEFT)

        # Detection parameters (editable)
        self.threshold_mV = tk.DoubleVar(value=20.0)   # mV
        self.min_gap_ms = tk.DoubleVar(value=150.0)    # ms
        self.pre_ms = tk.DoubleVar(value=20.0)         # ms
        self.post_ms = tk.DoubleVar(value=80.0)        # ms

        def labeled_entry(label, var, width=8):
            box = ttk.Frame(ctrl)
            box.pack(side=tk.LEFT, padx=10)
            ttk.Label(box, text=label).pack(side=tk.TOP, anchor="w")
            ttk.Entry(box, textvariable=var, width=width).pack(side=tk.TOP)

        labeled_entry("Threshold (mV)", self.threshold_mV)
        labeled_entry("Min gap (ms)", self.min_gap_ms)
        labeled_entry("Pre window (ms)", self.pre_ms)
        labeled_entry("Post window (ms)", self.post_ms)

        ttk.Button(ctrl, text="Re-run Detection", command=self.run_detection).pack(side=tk.LEFT, padx=10)
        ttk.Button(ctrl, text="Export Vpp Summary CSV", command=self.export_summary).pack(side=tk.LEFT)

        # Tabs
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tab_wave = ttk.Frame(self.nb)
        self.tab_trend = ttk.Frame(self.nb)
        self.tab_hist = ttk.Frame(self.nb)
        self.tab_stats = ttk.Frame(self.nb)

        self.nb.add(self.tab_wave, text="Waveform")
        self.nb.add(self.tab_trend, text="Vpp Trend")
        self.nb.add(self.tab_hist, text="Histogram")
        self.nb.add(self.tab_stats, text="Stats")

        # Matplotlib figures embedded in each tab
        self.fig_wave, self.ax_wave = plt.subplots()
        self.canvas_wave = FigureCanvasTkAgg(self.fig_wave, master=self.tab_wave)
        self.canvas_wave.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.fig_trend, self.ax_trend = plt.subplots()
        self.canvas_trend = FigureCanvasTkAgg(self.fig_trend, master=self.tab_trend)
        self.canvas_trend.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.fig_hist, self.ax_hist = plt.subplots()
        self.canvas_hist = FigureCanvasTkAgg(self.fig_hist, master=self.tab_hist)
        self.canvas_hist.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Stats text
        self.stats_text = tk.Text(self.tab_stats, height=20)
        self.stats_text.pack(fill=tk.BOTH, expand=True)

        self.set_stats("Open a CSV to begin.\n")

    def set_stats(self, s: str):
        self.stats_text.delete("1.0", tk.END)
        self.stats_text.insert(tk.END, s)

    def open_file(self):
        path = filedialog.askopenfilename(
            title="Select Rigol CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not path:
            return

        try:
            t, v, start, inc = read_rigol_csv(path)
        except Exception as e:
            messagebox.showerror("Read error", str(e))
            return

        self.filepath = path
        self.t = t
        self.v = v

        self.run_detection()

    def run_detection(self):
        if self.t is None or self.v is None:
            messagebox.showinfo("No data", "Open a CSV first.")
            return

        thr_v = self.threshold_mV.get() / 1000.0
        min_gap_s = self.min_gap_ms.get() / 1000.0
        pre_s = self.pre_ms.get() / 1000.0
        post_s = self.post_ms.get() / 1000.0

        self.events = detect_taps_and_vpp(
            self.t, self.v,
            threshold_v=thr_v,
            min_gap_s=min_gap_s,
            pre_s=pre_s,
            post_s=post_s
        )

        self.redraw_all()

    def redraw_all(self):
        # ---- Waveform tab ----
        self.ax_wave.clear()
        self.ax_wave.plot(self.t, self.v, linewidth=1)
        self.ax_wave.set_title("Voltage vs Time (detected taps marked)")
        self.ax_wave.set_xlabel("Time (s)")
        self.ax_wave.set_ylabel("Voltage (V)")

        # Mark detected tap centers
        for ev in self.events:
            tc = ev["time_center"]
            self.ax_wave.axvline(tc, linestyle="--", linewidth=1)

        self.fig_wave.tight_layout()
        self.canvas_wave.draw()

        # ---- Trend tab ----
        self.ax_trend.clear()
        if self.events:
            vpps = [ev["vpp"] for ev in self.events]
            x = np.arange(1, len(vpps) + 1)
            self.ax_trend.plot(x, vpps, marker="o", linewidth=1)
            self.ax_trend.set_title("Vpp per Tap")
            self.ax_trend.set_xlabel("Tap #")
            self.ax_trend.set_ylabel("Vpp (V)")
        else:
            self.ax_trend.set_title("Vpp per Tap (no events detected — lower threshold?)")
        self.fig_trend.tight_layout()
        self.canvas_trend.draw()

        # ---- Histogram tab ----
        self.ax_hist.clear()
        if self.events:
            vpps = np.array([ev["vpp"] for ev in self.events], dtype=float)
            bins = min(20, max(5, len(vpps)))
            self.ax_hist.hist(vpps, bins=bins)
            self.ax_hist.set_title("Vpp Distribution")
            self.ax_hist.set_xlabel("Vpp (V)")
            self.ax_hist.set_ylabel("Count")
        else:
            self.ax_hist.set_title("Histogram (no events detected)")
        self.fig_hist.tight_layout()
        self.canvas_hist.draw()

        # ---- Stats tab ----
        base = f"File: {os.path.basename(self.filepath) if self.filepath else '(none)'}\n"
        base += f"Samples: {len(self.v)}\n"
        base += f"Detected taps: {len(self.events)}\n"
        base += f"Threshold: {self.threshold_mV.get():.2f} mV | Min gap: {self.min_gap_ms.get():.1f} ms\n"
        base += f"Window: pre {self.pre_ms.get():.1f} ms, post {self.post_ms.get():.1f} ms\n\n"

        if self.events:
            vpps = np.array([ev["vpp"] for ev in self.events], dtype=float)
            mean = float(np.mean(vpps))
            std = float(np.std(vpps, ddof=1)) if len(vpps) > 1 else 0.0
            cv = float(std / mean) if mean != 0 else float("nan")
            base += f"Mean Vpp: {mean:.6f} V\n"
            base += f"Std Vpp:  {std:.6f} V\n"
            base += f"CV:       {cv:.4f}\n"
            base += "\nFirst 10 taps (Vpp):\n"
            for i, ev in enumerate(self.events[:10], start=1):
                base += f"  Tap {i:02d}: {ev['vpp']:.6f} V at t={ev['time_center']:.3f} s\n"
        else:
            base += "No taps detected.\nTry lowering threshold (mV) or checking your signal.\n"

        self.set_stats(base)

    def export_summary(self):
        if not self.events:
            messagebox.showinfo("Nothing to export", "No taps detected.")
            return
        if not self.filepath:
            messagebox.showinfo("No file", "Open a CSV first.")
            return

        # Save next to original CSV
        out_path = os.path.splitext(self.filepath)[0] + "_vpp_summary.csv"

        lines = ["tap_index,time_center_s,vpp_V\n"]
        for i, ev in enumerate(self.events, start=1):
            lines.append(f"{i},{ev['time_center']:.6f},{ev['vpp']:.9f}\n")

        with open(out_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        messagebox.showinfo("Export complete", f"Saved:\n{out_path}")


if __name__ == "__main__":
    app = RigolAnalyzerApp()
    app.mainloop()