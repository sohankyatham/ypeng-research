# ypeng_analysis.py
'''
1. Load data from CSV
2. Process signal
3. Compute statistics
4. Visualize results (generate plots)
'''
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class YPENGApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Y-PENG Statistical Variability Analyzer")
        self.geometry("1100x780")
        self.resizable(True, True)
        self.configure(bg="#f4f4f4")

        self.build_UI()

    def do_nothing():
        pass

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

        self.btn(btn_frame, "Add CSV Files", self.do_nothing, "#3a86ff").pack(side="left", padx=4)
        self.btn(btn_frame, "Clear Files", self.do_nothing, "#6c757d").pack(side="left", padx=4)
        self.btn(btn_frame, "Run Analysis", self.do_nothing, "#2dc653").pack(side="left", padx=4)
        self.btn(btn_frame, "Save Figures", self.do_nothing, "#ff6b35").pack(side="left", padx=4)

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
            self.file_listbox.pack(side="left", fill="x", expand=True)
            scrollbar.pack(side="right", fill="y")

            tk.Label(parent, text="(up to 4 CSV files)",
                 font=("Helvetica", 8), bg="#f4f4f4", fg="#888").pack(anchor="w")

            # Divider
            ttk.Separator(parent, orient="horizontal").pack(fill="x", pady=10)

            # Stats table
            tk.Label(parent, text="Results Summary", font=("Helvetica", 11, "bold"),
                    bg="#f4f4f4", fg="#222").pack(anchor="w", pady=(0, 4))

            cols = ("Trial", "Cycles", "Mean Vpp", "SD", "CV")
            self.stats_tree = ttk.Treeview(parent, columns=cols,
                                        show="headings", height=6)
            for col, width in zip(cols, [48, 52, 78, 64, 58]):
                self.stats_tree.heading(col, text=col)
                self.stats_tree.column(col, width=width, anchor="center")

            style = ttk.Style()
            style.configure("Treeview", font=("Helvetica", 9), rowheight=22)
            style.configure("Treeview.Heading", font=("Helvetica", 9, "bold"))

            self.stats_tree.pack(fill="x")

            tk.Label(parent, text="Mean Vpp / SD in Volts · CV in %",
                    font=("Helvetica", 8), bg="#f4f4f4", fg="#888").pack(anchor="w", pady=2)

    def build_right_panel(self, parent):
                pass        


    # ------ HELPER METHODS ------
    def btn(self, parent, text, command, bg):
        return tk.Button(parent, text=text, command=command,
                         bg=bg, fg="white", font=("Helvetica", 9, "bold"),
                         relief="flat", padx=10, pady=5, cursor="hand2",
                         activebackground=bg, activeforeground="white")
# Create and run the app
app = YPENGApp()
app.mainloop()