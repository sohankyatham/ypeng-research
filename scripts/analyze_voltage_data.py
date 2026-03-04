"""
YPENG / piezo oscilloscope analysis (Rigol DS1054Z CSV)

Improvements vs earlier version:
- No hardcoded filenames or folders
- Lets you pick one or multiple CSV files using a file dialog
- Robustly parses Rigol-style CSVs (tries multiple strategies)
- Computes Vpp for each selected file and summary stats
- Plots:
  - Overlay of up to N waveforms
  - Vpp vs tap index
  - Histogram of Vpp
- Exports a vpp_summary.csv next to the selected files (or in the same folder)

How to run:
  python ypeng_analysis_gui.py
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional, Tuple, List

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# File dialog (built-in)
import tkinter as tk
from tkinter import filedialog, messagebox


MAX_OVERLAY = 8       # number of waveforms to overlay
OUTLIER_Z = 3.0       # z-score threshold for outlier flagging


@dataclass
class Waveform:
    path: str
    t: np.ndarray
    v: np.ndarray

    @property
    def filename(self) -> str:
        return os.path.basename(self.path)

    @property
    def vpp(self) -> float:
        """Peak-to-peak voltage for this waveform."""
        return float(np.nanmax(self.v) - np.nanmin(self.v))


def _try_read_csv(path: str) -> pd.DataFrame:
    """
    Rigol CSVs sometimes include non-numeric header blocks.
    This tries common read strategies.
    """
    # Strategy 1: regular read
    try:
        return pd.read_csv(path)
    except Exception:
        pass

    # Strategy 2: read without headers, skip bad lines
    return pd.read_csv(path, header=None, engine="python", on_bad_lines="skip")


def _extract_time_voltage(df: pd.DataFrame) -> Optional[Tuple[np.ndarray, np.ndarray]]:
    """
    Extract time and voltage arrays from a DataFrame.

    Handles:
    - Named columns like Time/Voltage
    - Two numeric columns (first two numeric-rich columns)
    - Mixed header text lines (coerces to numeric and filters NaNs)
    """
    # Case A: has column names that look like time/voltage
    try:
        cols = [str(c).strip().lower() for c in df.columns]
        time_candidates = [i for i, c in enumerate(cols) if "time" in c or c in ("t", "x")]
        volt_candidates = [i for i, c in enumerate(cols) if "volt" in c or c in ("v", "y", "ch1")]

        if time_candidates and volt_candidates:
            tcol = df.columns[time_candidates[0]]
            vcol = df.columns[volt_candidates[0]]
            t = pd.to_numeric(df[tcol], errors="coerce").to_numpy()
            v = pd.to_numeric(df[vcol], errors="coerce").to_numpy()
            mask = np.isfinite(t) & np.isfinite(v)
            if mask.sum() > 10:
                return t[mask], v[mask]
    except Exception:
        pass

    # Case B: coerce everything numeric and pick two best columns
    dfn = df.copy()
    for c in dfn.columns:
        dfn[c] = pd.to_numeric(dfn[c], errors="coerce")

    good_cols = [c for c in dfn.columns if np.isfinite(dfn[c].to_numpy()).sum() > 10]
    if len(good_cols) >= 2:
        t = dfn[good_cols[0]].to_numpy()
        v = dfn[good_cols[1]].to_numpy()
        mask = np.isfinite(t) & np.isfinite(v)
        if mask.sum() > 10:
            return t[mask], v[mask]

    return None


def load_waveforms(paths: List[str]) -> List[Waveform]:
    waves: List[Waveform] = []
    for p in paths:
        df = _try_read_csv(p)
        extracted = _extract_time_voltage(df)
        if extracted is None:
            print(f"[WARN] Could not parse time/voltage from: {os.path.basename(p)}")
            continue
        t, v = extracted
        waves.append(Waveform(path=p, t=t, v=v))

    if not waves:
        raise RuntimeError("Parsed 0 waveforms. Your CSV format may differ from expected.")
    return waves


def pick_csv_files() -> List[str]:
    """Open a file dialog for selecting one or multiple CSV files."""
    root = tk.Tk()
    root.withdraw()  # hide the empty window
    root.attributes("-topmost", True)

    paths = filedialog.askopenfilenames(
        title="Select oscilloscope CSV file(s)",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )

    # askopenfilenames returns a tuple; convert to list
    return list(paths)


def main() -> None:
    paths = pick_csv_files()
    if not paths:
        # User cancelled
        print("No files selected. Exiting.")
        return

    waves = load_waveforms(paths)
    vpps = np.array([w.vpp for w in waves], dtype=float)

    mean_vpp = float(np.mean(vpps))
    std_vpp = float(np.std(vpps, ddof=1)) if len(vpps) > 1 else 0.0
    cv_vpp = float(std_vpp / mean_vpp) if mean_vpp != 0 else float("nan")

    print("\n=== Vpp summary (per CSV / per tap) ===")
    print(f"Files selected: {len(paths)}")
    print(f"Files parsed:   {len(waves)}")
    print(f"Mean Vpp:       {mean_vpp:.6f} V")
    print(f"Std Vpp:        {std_vpp:.6f} V")
    print(f"CV (Std/Mean):  {cv_vpp:.4f}")

    # Outlier flagging
    if len(vpps) >= 3 and std_vpp > 0:
        z = (vpps - mean_vpp) / std_vpp
        out_idx = np.where(np.abs(z) >= OUTLIER_Z)[0]
        if len(out_idx) > 0:
            print("\nOutliers (|z| >= {:.1f}):".format(OUTLIER_Z))
            for i in out_idx:
                print(f"  Tap #{i+1:03d}: {waves[i].filename}  Vpp={vpps[i]:.6f} V  z={z[i]:+.2f}")
        else:
            print("\nNo outliers flagged by z-score.")

    # --- Plot 1: Overlay waveforms ---
    plt.figure()
    for w in waves[:min(MAX_OVERLAY, len(waves))]:
        plt.plot(w.t, w.v, linewidth=1)
    plt.title(f"Waveform overlay (first {min(MAX_OVERLAY, len(waves))} taps)")
    plt.xlabel("Time (s)")
    plt.ylabel("Voltage (V)")
    plt.show()

    # --- Plot 2: Vpp vs tap index ---
    plt.figure()
    plt.plot(np.arange(1, len(vpps) + 1), vpps, marker="o", linewidth=1)
    plt.title("Vpp per tap")
    plt.xlabel("Tap index")
    plt.ylabel("Vpp (V)")
    plt.show()

    # --- Plot 3: Histogram of Vpp ---
    plt.figure()
    plt.hist(vpps, bins=min(15, max(5, len(vpps))))
    plt.title("Vpp distribution")
    plt.xlabel("Vpp (V)")
    plt.ylabel("Count")
    plt.show()

    # Save tidy summary CSV next to the first selected file
    out_dir = os.path.dirname(waves[0].path) if waves else os.path.dirname(paths[0])
    out_path = os.path.join(out_dir, "vpp_summary.csv")

    summary = pd.DataFrame({
        "tap_index": np.arange(1, len(waves) + 1),
        "filename": [w.filename for w in waves],
        "vpp_volts": vpps,
    })
    summary.to_csv(out_path, index=False)
    print(f"\nSaved summary: {out_path}")

    # Pop a small message box at end (optional convenience)
    try:
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo(
            "Done",
            f"Parsed {len(waves)} file(s).\n"
            f"Mean Vpp = {mean_vpp:.6f} V\n"
            f"Saved: {out_path}"
        )
        root.destroy()
    except Exception:
        pass


if __name__ == "__main__":
    main()