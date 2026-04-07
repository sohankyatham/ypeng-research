# ypeng_analysis.py
'''
1. Load data from CSV
2. Process signal
3. Compute statistics
4. Visualize results (generate plots)
'''
import tkinter as tk

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

    def btn(self, parent, text, command, bg):
        return tk.Button(parent, text=text, command=command,
                         bg=bg, fg="white", font=("Helvetica", 9, "bold"),
                         relief="flat", padx=10, pady=5, cursor="hand2",
                         activebackground=bg, activeforeground="white")
# Create and run the app
app = YPENGApp()
app.mainloop()