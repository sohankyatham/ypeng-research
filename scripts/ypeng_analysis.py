# ypeng_analysis.py
'''
1. Load data from CSV
2. Process signal
3. Compute statistics
4. Visualize results (generate plots)
'''
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

matplotlib.use("TkAgg")


# ----------------------------------
# ANALYSIS SETTINGS
# ----------------------------------

# Sliding window: 100 samples × 0.02 s/sample = 2 seconds per window
WINDOW_SAMPLES = 100
STEP_SAMPLES   = 50    # 50% overlap

COLORS = [
    "steelblue", "darkorange", "forestgreen", "crimson",
    "mediumpurple", "saddlebrown", "deeppink", "teal",
    "goldenrod", "slategray"
]

FIGURES_DIR = "figures"
os.makedirs(FIGURES_DIR, exist_ok=True)


# -------------------------
# ANALYSIS FUNCTIONS
# -------------------------

def load_csv(filepath):
    # Read the metadata row to get Start and Increment
    meta = pd.read_csv(filepath, nrows=1, header=0)
    try:
        time_start     = float(meta.columns[2])   # "Start" column header value
        time_increment = float(meta.columns[3])   # "Increment" column header value
    except (IndexError, ValueError):
        # Fallback defaults if header format is different
        time_start     = -11.78
        time_increment =  0.02

     # Read the actual data rows
    df = pd.read_csv(filepath, skiprows=1, usecols=[0, 1],
                     names=["sample", "voltage"], header=0)
    df["voltage"] = pd.to_numeric(df["voltage"], errors="coerce")
    df = df.dropna().reset_index(drop=True)
    df["time"] = time_start + df["sample"] * time_increment
    return df

def extract_vpp_per_window(voltage_array):
    vpps = [] # vpp = max - min
    v = voltage_array
    for i in range(0, len(v) - WINDOW_SAMPLES, STEP_SAMPLES):
        seg = v[i : i + WINDOW_SAMPLES]
        vpps.append(seg.max() - seg.min())
    return np.array(vpps)

# Compute and return the mean, sample standard deviation, and coefficient of variation (CV)
def compute_stats(vpps):
    mean = np.mean(vpps)
    std  = np.std(vpps, ddof=1)
    cv   = (std / mean) * 100 if mean != 0 else float("nan")
    return mean, std, cv

# Run full analysis pipeline on CSV files
def analyze_files(filepaths):
    results = []
    for i, fp in enumerate(filepaths):
        df             = load_csv(fp)
        vpps           = extract_vpp_per_window(df["voltage"].values)
        mean, std, cv  = compute_stats(vpps)
        results.append({
            "trial"    : i + 1,
            "label"    : f"Trial {i + 1}",
            "filename" : os.path.basename(fp),
            "df"       : df,
            "vpps"     : vpps,
            "mean"     : mean,
            "std"      : std,
            "cv"       : cv,
            "color"    : COLORS[i % len(COLORS)],
        })
    return results

def load_current_csv(filepath):
    # Sourcemeter format: tab-separated, no header, columns = time, current
    df = pd.read_csv(filepath, sep='\t', header=None, names=['time', 'current'])
    df['time']    = pd.to_numeric(df['time'],    errors='coerce')
    df['current'] = pd.to_numeric(df['current'], errors='coerce')
    df = df.dropna().reset_index(drop=True)
    return df

def analyze_current_files(filepaths):
    results = []
    for i, fp in enumerate(filepaths):
        df   = load_current_csv(fp)
        mean = df['current'].mean()
        std  = df['current'].std(ddof=1)
        peak = df['current'].abs().max()
        cv   = (std / abs(mean)) * 100 if mean != 0 else float('nan')
        results.append({
            'trial'    : i + 1,
            'label'    : f"Trial {i + 1}",
            'filename' : os.path.basename(fp),
            'df'       : df,
            'mean'     : mean,
            'std'      : std,
            'peak'     : peak,
            'cv'       : cv,
            'color'    : COLORS[i % len(COLORS)],
        })
    return results

def build_figure_current(results):
    n   = len(results)
    fig, axes = plt.subplots(n, 1, figsize=(9, 3.5 * n), sharex=False)
    if n == 1:
        axes = [axes]
    for ax, r in zip(axes, results):
        ax.plot(r['df']['time'], r['df']['current'],
                color=r['color'], linewidth=0.8, alpha=0.9)
        ax.axhline(0, color='gray', linewidth=0.6, linestyle='--')
        ax.axhline(r['mean'], color=r['color'], linewidth=1.2, linestyle='--',
                   label=f"Mean = {r['mean']:.4f} A")
        ax.set_ylabel("Current (A)", fontsize=10)
        ax.set_title(
            f"{r['label']} — {r['filename']}  |  "
            f"Peak = {r['peak']:.4f} A  |  CV = {r['cv']:.1f}%",
            fontsize=10, fontweight='bold')
        ax.legend(fontsize=8, loc='upper right')
        ax.tick_params(labelsize=9)
    axes[-1].set_xlabel("Time (s)", fontsize=10)
    fig.suptitle("Sourcemeter Current Output", fontsize=12, fontweight='bold')
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.subplots_adjust(hspace=0.55)
    return fig


# -------------------------
# BUILD FIGURES
# -------------------------

def build_figure_raw(results):
    # Figure 1 - Raw voltage traces, one subplot per trial
    n = len(results)
    fig, axes = plt.subplots(n, 1, figsize=(9, 3.5 * n), sharex=False)
    
    if n == 1:
        axes = [axes]
    
    for ax, r in zip(axes, results):
        ax.plot(r["df"]["time"], r["df"]["voltage"],
                color=r["color"], linewidth=0.8, alpha=0.9)
        ax.axhline(0, color="gray", linewidth=0.6, linestyle="--")
        ax.set_ylabel("Voltage (V)", fontsize=10)
        ax.set_title(f"{r['label']} — {r['filename']}", fontsize=10, fontweight="bold")
        ax.tick_params(labelsize=9)
    
    axes[-1].set_xlabel("Time (s)", fontsize=10)
    fig.suptitle("Raw Oscilloscope Voltage Signals",
                 fontsize=12, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.subplots_adjust(hspace=0.55)
    
    return fig


def build_figure_vpp(results):
    # Figure 2 — Cycle-by-cycle Vpp with mean ± SD band (KEY figure)
    n   = len(results)
    fig, axes = plt.subplots(n, 1, figsize=(9, 3.5 * n), sharex=False)

    if n == 1:
        axes = [axes]

    for ax, r in zip(axes, results):
        cycles = np.arange(1, len(r["vpps"]) + 1)
        ax.plot(cycles, r["vpps"], "o-", color=r["color"],
                markersize=4, linewidth=1.2, alpha=0.85)
        ax.axhline(r["mean"], color=r["color"], linewidth=1.5, linestyle="--",
                   label=f"Mean = {r['mean']:.3f} V")
        ax.fill_between(cycles,
                        r["mean"] - r["std"],
                        r["mean"] + r["std"],
                        color=r["color"], alpha=0.12,
                        label=f"±1 SD = {r['std']:.3f} V")
        ax.set_ylabel("Vpp (V)", fontsize=10)
        ax.set_title(f"{r['label']}  |  CV = {r['cv']:.1f}%",
                     fontsize=10, fontweight="bold")
        ax.legend(fontsize=8, loc="upper right")
        ax.set_ylim(bottom=0)
        ax.tick_params(labelsize=9)

    axes[-1].set_xlabel("Window (Cycle Number)", fontsize=10)
    fig.suptitle("Cycle-by-Cycle Peak-to-Peak Voltage (Vpp)",
                 fontsize=12, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.subplots_adjust(hspace=0.55)

    return fig


def build_figure_summary(results):
    # Figure 3 - Summary bar chart: mean Vpp +/- SD with CV labeled
    n = len(results)
    labels = [r["label"] for r in results]
    means = [r["mean"]  for r in results]
    stds = [r["std"]   for r in results]
    cvs = [r["cv"]    for r in results]

    fig, ax = plt.subplots(figsize=(max(5, 2 * n + 2), 4.5))
    x = np.arange(n)
    colors = [r["color"] for r in results]
    bars = ax.bar(x, means, yerr=stds, capsize=6,
                  color=colors, alpha=0.80,
                  error_kw={"linewidth": 1.8, "ecolor": "black"})
    
    for bar, std, cv in zip(bars, stds, cvs):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + std + 0.003,
                f"CV = {cv:.1f}%",
                ha="center", va="bottom", fontsize=9, fontweight="bold")
    
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylabel("Mean Vpp (V)", fontsize=12)
    ax.set_title("Mean Peak-to-Peak Voltage per Trial\n(Error bars = ±1 SD)",
                 fontsize=11, fontweight="bold")
    ax.set_ylim(bottom=0)
    ax.tick_params(labelsize=10)
    fig.tight_layout()
    
    return fig


# -------------------------
# USER INTERFACE
# -------------------------

class YPENGApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Y-PENG Statistical Variability Analyzer")
        self.geometry("1100x780")
        self.resizable(True, True)
        self.configure(bg="#f4f4f4")

        self.loaded_files = []   # list of filepath strings
        self.results      = []   # list of result dicts after analysis
        self.current_files  = []
        self.current_results = []

        self.build_UI()

    # Construct User Interface
    def build_UI(self):
        # Create the control panel at the top 
        ctrl = tk.Frame(self, bg="#2b2b2b", pady=10)

        ctrl.pack(fill="x")

        tk.Label(ctrl, text="Y-PENG Statistical Variability Analyzer",
                 font=("Helvetica", 15, "bold"),
                 fg="white", bg="#2b2b2b").pack(side="left", padx=16)

        # Buttons (right side of header)
        btn_frame = tk.Frame(ctrl, bg="#2b2b2b")
        btn_frame.pack(side="right", padx=12)

        self.btn(btn_frame, "Add CSV Files", self.add_files, "#3a86ff").pack(side="left", padx=4)
        self.btn(btn_frame, "Add Current Files", self.add_current_files, "#7b2ff7").pack(side="left", padx=4)
        self.btn(btn_frame, "Remove Selected", self.remove_selected, "#6c757d").pack(side="left", padx=4)
        self.btn(btn_frame, "Clear All", self.clear_files, "#6c757d").pack(side="left", padx=4)
        self.btn(btn_frame, "Run Analysis", self.run_analysis, "#2dc653").pack(side="left", padx=4)
        self.btn(btn_frame, "Run Current Analysis", self.run_current_analysis, "#7b2ff7").pack(side="left", padx=4)
        self.btn(btn_frame, "Save Figures", self.save_figures, "#ff6b35").pack(side="left", padx=4)

        # Main Area: left panel & right tabs
        main = tk.Frame(self, bg="#f4f4f4")
        main.pack(fill="both", expand=True, padx=10, pady=8)

        # Left panel - file list + results table with stats
        left = tk.Frame(main, bg="#f4f4f4", width=300)
        left.pack(side="left", fill="y", padx=(0, 8))
        left.pack_propagate(False)

        self.build_left_panel(left)

        # Right panel - tabbed figures
        right = tk.Frame(main, bg="#f4f4f4")
        right.pack(side="left", fill="both", expand=True)

        self.build_right_panel(right)

        # Status bar 
        self.status_var = tk.StringVar(value="Ready — add CSV files to begin.")
        tk.Label(self, textvariable=self.status_var,
                 anchor="w", bg="#e0e0e0", fg="#333",
                 font=("Helvetica", 9), pady=3, padx=8).pack(fill="x", side="bottom")


    def build_left_panel(self, parent):
            # File list
            tk.Label(parent, text="Loaded Files", font=("Helvetica", 11, "bold"),
                    bg="#f4f4f4", fg="#222").pack(anchor="w", pady=(0, 4))

            list_frame = tk.Frame(parent, bg="#f4f4f4")
            list_frame.pack(fill="x")

            # Create scrollbar for left panel
            scrollbar = tk.Scrollbar(list_frame, orient="vertical")
            self.file_listbox = tk.Listbox(
                list_frame, height=8, yscrollcommand=scrollbar.set,
                font=("Courier", 9), selectmode="single",
                bg="white", relief="flat", bd=1,
                highlightthickness=1, highlightbackground="#ccc")
            scrollbar.config(command=self.file_listbox.yview)
            self.file_listbox.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            list_frame.pack(fill="both", expand=True)

            tk.Label(parent, text="(Select any number of CSV files)",
                 font=("Helvetica", 8), bg="#f4f4f4", fg="#888").pack(anchor="w")

            # Divider
            ttk.Separator(parent, orient="horizontal").pack(fill="x", pady=10)

            # Stats table
            tk.Label(parent, text="Results Summary", font=("Helvetica", 11, "bold"),
                    bg="#f4f4f4", fg="#222").pack(anchor="w", pady=(0, 4))

            cols = ("Trial", "Cycles", "Mean Vpp", "SD", "CV")
            tree_frame = tk.Frame(parent, bg="#f4f4f4")
            tree_frame.pack(fill="x")

            tree_scroll = tk.Scrollbar(tree_frame, orient="vertical")
            self.stats_tree = ttk.Treeview(tree_frame, columns=cols,
                                        show="headings", height=6,
                                        yscrollcommand=tree_scroll.set)
            tree_scroll.config(command=self.stats_tree.yview)

            for col, width in zip(cols, [48, 52, 78, 64, 58]):
                self.stats_tree.heading(col, text=col)
                self.stats_tree.column(col, width=width, anchor="center")

            style = ttk.Style()
            style.configure("Treeview", font=("Helvetica", 9), rowheight=22)
            style.configure("Treeview.Heading", font=("Helvetica", 9, "bold"))

            self.stats_tree.pack(side="left", fill="x", expand=True)
            tree_scroll.pack(side="right", fill="y")

            tk.Label(parent, text="Mean Vpp / SD in Volts · CV in %",
                    font=("Helvetica", 8), bg="#f4f4f4", fg="#888").pack(anchor="w", pady=2)

    def build_right_panel(self, parent):
        # Create tabs
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill="both", expand=True)        

        self.tab_vpp = tk.Frame(self.notebook, bg="white")
        self.tab_raw = tk.Frame(self.notebook, bg="white")
        self.tab_summary = tk.Frame(self.notebook, bg="white")
        self.tab_current = tk.Frame(self.notebook, bg="white")

        self.notebook.add(self.tab_vpp, text="  Cycle Vpp  ")
        self.notebook.add(self.tab_raw, text="  Raw Signal  ")
        self.notebook.add(self.tab_summary, text="  Summary Bar  ")
        self.notebook.add(self.tab_current, text="  Current (A)  ")

        # Placeholder labels until analysis runs
        for tab, msg in [
            (self.tab_vpp, "Run analysis to see cycle-by-cycle Vpp plot"),
            (self.tab_raw, "Run analysis to see raw voltage traces"),
            (self.tab_summary, "Run analysis to see summary bar chart"),
            (self.tab_current, "Add current CSV files and click Run Current Analysis"),
        ]:
            tk.Label(tab, text=msg, font=("Helvetica", 11),
                     fg="#aaa", bg="white").place(relx=0.5, rely=0.5, anchor="center")

        self.canvas_vpp = None
        self.canvas_raw = None
        self.canvas_summary = None
        self.canvas_current = None

    # Button Callbacks

    def add_files(self):
        fps = filedialog.askopenfilenames(
        title=f"Select CSV file(s)",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])

        added = 0
        for fp in fps:
            if fp not in self.loaded_files:
                self.loaded_files.append(fp)
                self.file_listbox.insert("end", os.path.basename(fp))
                added += 1

        if added:
            self.status_var.set(f"{added} file(s) added — {len(self.loaded_files)} loaded. Click Run Analysis.")
        else:
            self.status_var.set("No new files added.")

    def clear_files(self):
        self.loaded_files.clear()
        self.results.clear()
        self.file_listbox.delete(0, "end")
        for row in self.stats_tree.get_children():
            self.stats_tree.delete(row)
        self.status_var.set("Files cleared. Add new CSV files to begin.")

    def remove_selected(self):
        selected = list(self.file_listbox.curselection())
        if not selected:
            messagebox.showinfo("Nothing selected", "Click a file in the list first.")
            return
        for i in reversed(selected):
            self.file_listbox.delete(i)
            del self.loaded_files[i]
        self.status_var.set(f"Removed {len(selected)} file(s). {len(self.loaded_files)} remaining.")

    def run_analysis(self):
        if not self.loaded_files:
            messagebox.showwarning("No files", "Please add at least one CSV file first.")
            return

        self.status_var.set("Running analysis…")
        self.update_idletasks()

        try:
            self.results = analyze_files(self.loaded_files)
        except Exception as e:
            messagebox.showerror("Analysis error", str(e))
            self.status_var.set("Analysis failed - see error dialog.")
            return

        self.populate_stats_table()
        self.draw_figures()
        self.status_var.set(
            f"Analysis complete - {len(self.results)} trial(s) processed. "
            "Use Save Figures to export PNGs.")

    def save_figures(self):
        if not self.results:
            messagebox.showwarning("No results", "Run analysis first.")
            return
        
        save_dir = filedialog.askdirectory(title="Select folder to save figures")
        if not save_dir:
            return
        
        build_figure_raw(self.results).savefig(
            os.path.join(save_dir, "fig1_raw_trace.png"), dpi=200, bbox_inches="tight")
        build_figure_vpp(self.results).savefig(
            os.path.join(save_dir, "fig2_vpp_per_cycle.png"), dpi=200, bbox_inches="tight")
        build_figure_summary(self.results).savefig(
            os.path.join(save_dir, "fig3_summary_bar.png"), dpi=200, bbox_inches="tight")
        plt.close("all")

        messagebox.showinfo("Saved", f"3 figures saved to:\n{save_dir}")
        self.status_var.set(f"Figures saved to {save_dir}")


    # -------------------------
    # HELPER FUNCTIONS 
    # -------------------------

    def btn(self, parent, text, command, bg):
        return tk.Button(parent, text=text, command=command,
                         bg=bg, fg="white", font=("Helvetica", 9, "bold"),
                         relief="flat", padx=10, pady=5, cursor="hand2",
                         activebackground=bg, activeforeground="white")

    def populate_stats_table(self):
        for row in self.stats_tree.get_children():
            self.stats_tree.delete(row)
        for r in self.results:
            self.stats_tree.insert("", "end", values=(
                r["label"],
                len(r["vpps"]),
                f"{r['mean']:.4f} V",
                f"{r['std']:.4f} V",
                f"{r['cv']:.1f}%",
            ))

    def add_current_files(self):
        fps = filedialog.askopenfilenames(
            title="Select current CSV file(s) from sourcemeter",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        added = 0
        for fp in fps:
            if fp not in self.current_files:
                self.current_files.append(fp)
                added += 1
        if added:
            self.status_var.set(f"{added} current file(s) added — {len(self.current_files)} total. Click Run Current Analysis.")
        else:
            self.status_var.set("No new current files added.")
    
    def run_current_analysis(self):
        if not self.current_files:
            messagebox.showwarning("No files", "Please add current CSV files first.")
            return
        self.status_var.set("Analyzing current data...")
        self.update_idletasks()
        try:
            self.current_results = analyze_current_files(self.current_files)
        except Exception as e:
            messagebox.showerror("Analysis error", str(e))
            self.status_var.set("Current analysis failed — see error dialog.")
            return
        self.draw_current_figure()
        self.status_var.set(f"Current analysis complete — {len(self.current_results)} trial(s) processed.")

    def draw_current_figure(self):
        tab = self.tab_current
        old = self.canvas_current
        if old:
            old.get_tk_widget().destroy()
        for widget in tab.winfo_children():
            widget.destroy()

        fig = build_figure_current(self.current_results)

        scroll_y = tk.Scrollbar(tab, orient="vertical")
        scroll_x = tk.Scrollbar(tab, orient="horizontal")
        scroll_y.pack(side="right",  fill="y")
        scroll_x.pack(side="bottom", fill="x")

        tk_canvas = tk.Canvas(tab, yscrollcommand=scroll_y.set,
                              xscrollcommand=scroll_x.set, bg="white")
        tk_canvas.pack(side="left", fill="both", expand=True)
        scroll_y.config(command=tk_canvas.yview)
        scroll_x.config(command=tk_canvas.xview)

        mpl_canvas = FigureCanvasTkAgg(fig, master=tk_canvas)
        mpl_canvas.draw()
        mpl_widget = mpl_canvas.get_tk_widget()
        tk_canvas.create_window((0, 0), window=mpl_widget, anchor="nw")

        def update_scrollregion(event, c=tk_canvas):
            c.configure(scrollregion=c.bbox("all"))
        mpl_widget.bind("<Configure>", update_scrollregion)

        def on_mousewheel(event, c=tk_canvas):
            c.yview_scroll(int(-1 * (event.delta / 120)), "units")
        tk_canvas.bind("<MouseWheel>", on_mousewheel)
        mpl_widget.bind("<MouseWheel>", on_mousewheel)

        self.canvas_current = mpl_canvas
        plt.close(fig)

    # Render every figure into its notebook tab
    def draw_figures(self):
        for canvas_attr, tab, build_fn in [
            ("canvas_vpp",     self.tab_vpp,     build_figure_vpp),
            ("canvas_raw",     self.tab_raw,     build_figure_raw),
            ("canvas_summary", self.tab_summary, build_figure_summary),
        ]:
            # Clear old widgets if re-running
            old = getattr(self, canvas_attr)
            if old:
                old.get_tk_widget().destroy()
            for widget in tab.winfo_children():
                widget.destroy()

            # Build figure
            fig = build_fn(self.results)
            n   = len(self.results)

            # Scrollable container
            scroll_y = tk.Scrollbar(tab, orient="vertical")
            scroll_x = tk.Scrollbar(tab, orient="horizontal")
            scroll_y.pack(side="right",  fill="y")
            scroll_x.pack(side="bottom", fill="x")

            tk_canvas = tk.Canvas(tab,
                                  yscrollcommand=scroll_y.set,
                                  xscrollcommand=scroll_x.set,
                                  bg="white")
            tk_canvas.pack(side="left", fill="both", expand=True)
            scroll_y.config(command=tk_canvas.yview)
            scroll_x.config(command=tk_canvas.xview)

            # Embed matplotlib figure into the tk canvas
            mpl_canvas = FigureCanvasTkAgg(fig, master=tk_canvas)
            mpl_canvas.draw()
            mpl_widget = mpl_canvas.get_tk_widget()
            tk_canvas.create_window((0, 0), window=mpl_widget, anchor="nw")

            # Update scroll region once the widget is drawn
            def update_scrollregion(event, c=tk_canvas):
                c.configure(scrollregion=c.bbox("all"))
            mpl_widget.bind("<Configure>", update_scrollregion)

            # Mouse wheel scrolling
            def on_mousewheel(event, c=tk_canvas):
                c.yview_scroll(int(-1 * (event.delta / 120)), "units")
            tk_canvas.bind("<MouseWheel>", on_mousewheel)
            mpl_widget.bind("<MouseWheel>", on_mousewheel)

            setattr(self, canvas_attr, mpl_canvas)
            plt.close(fig)

# Entry point
if __name__ == "__main__":
    app = YPENGApp()
    app.mainloop()