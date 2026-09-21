"""A compact always-on-top countdown timer for Windows. Requires Python 3 only."""

import time
import tkinter as tk
from tkinter import ttk


class CountdownApp:
    BG = "#111827"
    PANEL = "#1f2937"
    TEXT = "#f9fafb"
    MUTED = "#94a3b8"
    ACCENT = "#38bdf8"
    DANGER = "#fb7185"

    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("倒计时")
        root.geometry("330x255+12+12")
        root.minsize(330, 255)
        root.configure(bg=self.BG)
        root.attributes("-topmost", True)
        root.overrideredirect(True)
        root.protocol("WM_DELETE_WINDOW", root.destroy)

        self.running = False
        self.paused = False
        self.end_time = 0.0
        self.remaining = 5 * 60
        self.drag_x = self.drag_y = 0

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Timer.Horizontal.TScale", background=self.BG, troughcolor="#334155")
        style.configure("TEntry", fieldbackground=self.PANEL, foreground=self.TEXT, insertcolor=self.TEXT,
                        bordercolor="#475569", lightcolor="#475569", darkcolor="#475569")

        self._build()
        self._set_opacity()
        self._render_time()
        self._tick()

    def _build(self):
        # Moveable header keeps the timer unobtrusive without a normal title bar.
        header = tk.Frame(self.root, bg=self.BG, height=34)
        header.pack(fill="x", padx=14, pady=(10, 0))
        header.pack_propagate(False)
        title = tk.Label(header, text="●  专注倒计时", bg=self.BG, fg=self.ACCENT,
                         font=("Microsoft YaHei UI", 10, "bold"), anchor="w")
        title.pack(side="left", fill="y")
        for widget in (header, title):
            widget.bind("<ButtonPress-1>", self._drag_start)
            widget.bind("<B1-Motion>", self._drag_move)

        tk.Button(header, text="×", command=self.root.destroy, bg=self.BG, fg=self.MUTED,
                  activebackground=self.BG, activeforeground=self.TEXT, relief="flat", bd=0,
                  font=("Segoe UI", 16), cursor="hand2").pack(side="right")

        self.time_label = tk.Label(self.root, bg=self.BG, fg=self.TEXT, font=("Segoe UI", 40, "bold"))
        self.time_label.pack(pady=(0, 5))

        entry_row = tk.Frame(self.root, bg=self.BG)
        entry_row.pack()
        self.minute_var = tk.StringVar(value="05")
        self.second_var = tk.StringVar(value="00")
        self._entry(entry_row, self.minute_var).pack(side="left")
        tk.Label(entry_row, text="分", bg=self.BG, fg=self.MUTED, font=("Microsoft YaHei UI", 9)).pack(side="left", padx=(4, 10))
        self._entry(entry_row, self.second_var).pack(side="left")
        tk.Label(entry_row, text="秒", bg=self.BG, fg=self.MUTED, font=("Microsoft YaHei UI", 9)).pack(side="left", padx=(4, 0))

        buttons = tk.Frame(self.root, bg=self.BG)
        buttons.pack(pady=12)
        self.start_btn = self._button(buttons, "开始", self.toggle, self.ACCENT, "#082f49")
        self.start_btn.pack(side="left", padx=4)
        self._button(buttons, "重置", self.reset, self.MUTED, self.PANEL).pack(side="left", padx=4)

        bottom = tk.Frame(self.root, bg=self.BG)
        bottom.pack(fill="x", padx=20)
        tk.Label(bottom, text="透明度", bg=self.BG, fg=self.MUTED, font=("Microsoft YaHei UI", 8)).pack(side="left")
        self.opacity = tk.DoubleVar(value=0.94)
        ttk.Scale(bottom, variable=self.opacity, from_=0.35, to=1.0, orient="horizontal",
                  style="Timer.Horizontal.TScale", command=self._set_opacity).pack(side="left", fill="x", expand=True, padx=8)
        self.opacity_text = tk.Label(bottom, text="94%", bg=self.BG, fg=self.MUTED, font=("Segoe UI", 8))
        self.opacity_text.pack(side="right")

    def _entry(self, parent, variable):
        return ttk.Entry(parent, textvariable=variable, justify="center", width=3, font=("Segoe UI", 11, "bold"))

    def _button(self, parent, text, command, fg, bg):
        return tk.Button(parent, text=text, command=command, width=8, bg=bg, fg=fg,
                         activebackground=bg, activeforeground=self.TEXT, relief="flat", bd=0,
                         font=("Microsoft YaHei UI", 9, "bold"), cursor="hand2", pady=4)

    def _set_opacity(self, _=None):
        value = self.opacity.get()
        self.root.attributes("-alpha", value)
        self.opacity_text.config(text=f"{value:.0%}")

    def _drag_start(self, event):
        self.drag_x, self.drag_y = event.x_root, event.y_root

    def _drag_move(self, event):
        x = self.root.winfo_x() + event.x_root - self.drag_x
        y = self.root.winfo_y() + event.y_root - self.drag_y
        self.root.geometry(f"+{max(0, x)}+{max(0, y)}")
        self.drag_x, self.drag_y = event.x_root, event.y_root

    def _read_duration(self):
        try:
            minutes = max(0, int(self.minute_var.get() or 0))
            seconds = max(0, min(59, int(self.second_var.get() or 0)))
            return minutes * 60 + seconds
        except ValueError:
            return 0

    def toggle(self):
        if self.running:
            self.remaining = max(0, self.end_time - time.monotonic())
            self.running = False
            self.paused = self.remaining > 0
            self.start_btn.config(text="继续")
        else:
            if not self.paused:
                self.remaining = self._read_duration()
            if self.remaining > 0:
                self.end_time = time.monotonic() + self.remaining
                self.running = True
                self.paused = False
                self.time_label.config(fg=self.TEXT)
                self._render_time()
                self.start_btn.config(text="暂停")

    def reset(self):
        self.running = False
        self.paused = False
        self.remaining = self._read_duration()
        self.start_btn.config(text="开始")
        self.time_label.config(fg=self.TEXT)
        self._render_time()

    def _render_time(self):
        whole = max(0, int(self.remaining + 0.999))
        self.time_label.config(text=f"{whole // 60:02d}:{whole % 60:02d}")

    def _tick(self):
        if self.running:
            self.remaining = self.end_time - time.monotonic()
            if self.remaining <= 0:
                self.remaining = 0
                self.running = False
                self.start_btn.config(text="开始")
                self.root.bell()
                self.time_label.config(fg=self.DANGER)
            else:
                self.time_label.config(fg=self.TEXT)
            self._render_time()
        self.root.after(100, self._tick)


if __name__ == "__main__":
    app = tk.Tk()
    CountdownApp(app)
    app.mainloop()
