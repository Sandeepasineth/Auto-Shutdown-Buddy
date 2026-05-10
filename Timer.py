"""
Safe Auto Shutdown Timer (Python / Tkinter)
Windows 11 | Non-forced shutdown | Apps save data safely
"""

import tkinter as tk
from tkinter import messagebox
import subprocess
import random
import ctypes
import sys
import os

# ═══════════════════════════════════════════════════════════════
#  ADMIN ELEVATION
# ═══════════════════════════════════════════════════════════════
def _is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def _relaunch_as_admin() -> None:
    script = os.path.abspath(sys.argv[0])
    params = f'"{script}"'
    ret = ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, params, None, 1
    )
    if ret <= 32:
        ctypes.windll.user32.MessageBoxW(
            0,
            "Administrator privileges are required.\n\n"
            "Please right-click and choose 'Run as administrator'.",
            "Elevation Failed",
            0x10
        )
    sys.exit(0)


if not _is_admin():
    _relaunch_as_admin()


# ═══════════════════════════════════════════════════════════════
#  THEME PALETTE
# ═══════════════════════════════════════════════════════════════
CLR_BG              = "#000000"
CLR_TEXT            = "#16FF00"
CLR_TEXT_DIM        = "#0A8000"
CLR_TEXT_VDIM       = "#054000"
CLR_ACCENT          = "#00FFCC"
CLR_INPUT_BG        = "#061200"
CLR_INPUT_BORDER    = "#0A3D00"
CLR_BTN_BG          = "#0A1A00"
CLR_BTN_PRESS       = "#1A5000"
CLR_PROGRESS_FILL   = "#16FF00"
CLR_PROGRESS_GLOW   = "#0A8000"
CLR_PROGRESS_BG     = "#060E00"
CLR_PROGRESS_BORDER = "#0A3D00"
CLR_WARNING         = "#FFAA00"
CLR_ERROR           = "#FF3333"
CLR_SUCCESS         = "#00FF88"
CLR_SEPARATOR       = "#0A3D00"
CLR_BORDER          = "#083000"

# ═══════════════════════════════════════════════════════════════
#  SAFETY CONSTANTS
# ═══════════════════════════════════════════════════════════════
MIN_SECS          = 60
MAX_SECS          = 86400
CONFIRM_THRESHOLD = 300

MATRIX_CHARS = "0123456789ABCDEF@#$%&<>{}[]|/\\!?"
MATRIX_ROWS  = 42


# ═══════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════
class ShutdownTimerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Safe Shutdown Timer  [Administrator]")
        self.root.geometry("540x540")
        self.root.resizable(False, False)
        self.root.configure(bg=CLR_BG)

        self.state             = "IDLE"
        self.total_seconds     = 0
        self.remaining_seconds = 0
        self.blink_on          = True
        self._urgent_blink     = True

        self.confirm_timer      = None
        self.countdown_timer    = None
        self._reset_delay_timer = None

        self.matrix_left  = [[' '] * MATRIX_ROWS for _ in range(6)]
        self.matrix_right = [[' '] * MATRIX_ROWS for _ in range(6)]

        self._build_ui()
        self._start_blink()
        self._start_matrix()

    # ───────────────────────────────────────────────────────────
    #  UI
    # ───────────────────────────────────────────────────────────
    def _build_ui(self) -> None:
        self.matrix_canvas = tk.Canvas(
            self.root, width=540, height=540,
            bg=CLR_BG, highlightthickness=0
        )
        self.matrix_canvas.place(x=0, y=0)

        self.frame = tk.Frame(self.root, bg=CLR_BG)
        self.frame.place(x=0, y=0, width=540, height=540)

        self.title_label = tk.Label(
            self.frame, text="SAFE SHUTDOWN TIMER_",
            font=("Consolas", 22, "bold"), fg=CLR_TEXT, bg=CLR_BG
        )
        self.title_label.pack(pady=(18, 0))

        tk.Label(
            self.frame, text="[ RUNNING AS ADMINISTRATOR ]",
            font=("Consolas", 8), fg=CLR_ACCENT, bg=CLR_BG
        ).pack()

        self._pack_separator()

        # Time input
        input_frame = tk.Frame(self.frame, bg=CLR_BG)
        input_frame.pack(pady=(10, 0))

        tk.Label(
            input_frame, text="> TIME:",
            font=("Consolas", 13), fg=CLR_ACCENT, bg=CLR_BG
        ).pack(side=tk.LEFT, padx=(20, 10))

        self.time_entry = tk.Entry(
            input_frame, width=8, font=("Consolas", 14),
            fg=CLR_TEXT, bg=CLR_INPUT_BG,
            insertbackground=CLR_TEXT,
            relief=tk.FLAT, justify=tk.CENTER,
            highlightthickness=1,
            highlightbackground=CLR_INPUT_BORDER,
            highlightcolor=CLR_TEXT
        )
        self.time_entry.insert(0, "30")
        self.time_entry.pack(side=tk.LEFT, padx=5)

        # Unit radio buttons
        unit_frame = tk.Frame(self.frame, bg=CLR_BG)
        unit_frame.pack(pady=(8, 0))

        tk.Label(
            unit_frame, text="Unit:",
            font=("Consolas", 12), fg=CLR_ACCENT, bg=CLR_BG
        ).pack(side=tk.LEFT, padx=(80, 10))

        self.unit_var = tk.StringVar(value="min")
        for label_text, val in [("Sec", "sec"), ("Min", "min"), ("Hour", "hr")]:
            tk.Radiobutton(
                unit_frame, text=label_text,
                variable=self.unit_var, value=val,
                font=("Consolas", 11), fg=CLR_TEXT, bg=CLR_BG,
                selectcolor=CLR_BTN_BG, activebackground=CLR_BG,
                activeforeground=CLR_ACCENT, indicatoron=0,
                relief=tk.FLAT, bd=2, padx=8, pady=2,
                highlightbackground=CLR_BORDER
            ).pack(side=tk.LEFT, padx=5)

        # Buttons
        btn_frame = tk.Frame(self.frame, bg=CLR_BG)
        btn_frame.pack(pady=(16, 0))

        self.sched_btn = tk.Button(
            btn_frame, text=" SCHEDULE ",
            font=("Consolas", 14, "bold"),
            fg=CLR_TEXT, bg=CLR_BTN_BG,
            activebackground=CLR_BTN_PRESS,
            activeforeground=CLR_TEXT,
            relief=tk.FLAT, bd=2, cursor="hand2",
            command=self._on_schedule
        )
        self.sched_btn.pack(side=tk.LEFT, padx=10)

        self.cancel_btn = tk.Button(
            btn_frame, text="  CANCEL  ",
            font=("Consolas", 14, "bold"),
            fg=CLR_TEXT, bg=CLR_BTN_BG,
            activebackground=CLR_BTN_PRESS,
            activeforeground=CLR_TEXT,
            relief=tk.FLAT, bd=2, cursor="hand2",
            command=self._on_cancel
        )
        self.cancel_btn.pack(side=tk.LEFT, padx=10)

        self._pack_separator()

        # Progress label
        prog_label_frame = tk.Frame(self.frame, bg=CLR_BG)
        prog_label_frame.pack(pady=(10, 0), fill=tk.X, padx=30)

        tk.Label(
            prog_label_frame, text="[PROGRESS]",
            font=("Consolas", 10), fg=CLR_TEXT_DIM, bg=CLR_BG
        ).pack(side=tk.LEFT)

        self.pct_label = tk.Label(
            prog_label_frame, text="",
            font=("Consolas", 10), fg=CLR_TEXT, bg=CLR_BG
        )
        self.pct_label.pack(side=tk.RIGHT)

        # Progress bar
        self.progress_canvas = tk.Canvas(
            self.frame, width=480, height=22,
            bg=CLR_PROGRESS_BG, highlightthickness=1,
            highlightbackground=CLR_PROGRESS_BORDER
        )
        self.progress_canvas.pack(pady=(4, 0), padx=30)

        # Countdown
        self.countdown_label = tk.Label(
            self.frame, text="00:00:00",
            font=("Consolas", 36, "bold"),
            fg=CLR_TEXT_VDIM, bg=CLR_BG
        )
        self.countdown_label.pack(pady=(10, 0))

        self._pack_separator()

        # Status
        self.status_label = tk.Label(
            self.frame, text=">> Ready. Enter time and schedule.",
            font=("Consolas", 11), fg=CLR_TEXT_DIM, bg=CLR_BG
        )
        self.status_label.pack(pady=(7, 0))

        self._pack_separator()

        # Info
        for line in [
            "> Safe:      Apps save data before exit",
            "> Cancel:    'shutdown /a' in terminal",
            "> Range:     1 min  --  24 hours",
            "> Non-force: No data loss guaranteed",
        ]:
            tk.Label(
                self.frame, text=line,
                font=("Consolas", 9), fg=CLR_TEXT_VDIM, bg=CLR_BG
            ).pack(anchor=tk.W, padx=30)

        tk.Label(
            self.root, text="[v1.2] Win11 Safe",
            font=("Consolas", 8), fg=CLR_TEXT_VDIM, bg=CLR_BG
        ).place(x=405, y=522)

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _pack_separator(self) -> None:
        tk.Frame(self.frame, height=1, bg=CLR_SEPARATOR).pack(
            fill=tk.X, padx=20, pady=(6, 0)
        )

    # ───────────────────────────────────────────────────────────
    #  MATRIX RAIN
    # ───────────────────────────────────────────────────────────
    def _start_matrix(self) -> None:
        self._tick_matrix()

    def _tick_matrix(self) -> None:
        self.matrix_canvas.delete("all")

        for side in ("left", "right"):
            columns = self.matrix_left if side == "left" else self.matrix_right
            for col_idx, column in enumerate(columns):
                column.pop(0)
                column.append(
                    random.choice(MATRIX_CHARS) if random.random() > 0.4 else ' '
                )
                for row, char in enumerate(column):
                    if char == ' ':
                        continue
                    y_pos = row * 13
                    if y_pos > 540:
                        continue
                    dist = (MATRIX_ROWS - 1) - row
                    color = (
                        CLR_ACCENT    if dist == 0 else
                        CLR_TEXT      if dist <= 2 else
                        CLR_TEXT_DIM  if dist <= 5 else
                        CLR_TEXT_VDIM
                    )
                    x_pos = (
                        6   + col_idx * 12 if side == "left"
                        else 474 + col_idx * 12
                    )
                    self.matrix_canvas.create_text(
                        x_pos, y_pos, text=char,
                        fill=color, font=("Consolas", 9)
                    )

        self.root.after(110, self._tick_matrix)

    # ───────────────────────────────────────────────────────────
    #  BLINK
    # ───────────────────────────────────────────────────────────
    def _start_blink(self) -> None:
        self._tick_blink()

    def _tick_blink(self) -> None:
        self.blink_on = not self.blink_on
        self.title_label.config(
            text=f"SAFE SHUTDOWN TIMER{'_' if self.blink_on else ' '}"
        )
        self.root.after(530, self._tick_blink)

    # ───────────────────────────────────────────────────────────
    #  SHUTDOWN HELPERS  ← THE CORE FIX IS HERE
    # ───────────────────────────────────────────────────────────
    def _run_shutdown(self, args: list) -> bool:
        """
        FIX: Accept a ready-made list of arguments instead of a string.
        Never call .split() on arguments that may contain spaces/quotes.

        Uses CREATE_NO_WINDOW (0x08000000) to suppress the CMD flash.
        Captures stderr so we can show a meaningful error if it fails.
        """
        try:
            result = subprocess.run(
                ["shutdown"] + args,        # ← clean list, no string splitting
                creationflags=0x08000000,   # CREATE_NO_WINDOW
                capture_output=True,        # grab stdout + stderr
                text=True
            )

            if result.returncode != 0:
                # Show the actual error message from shutdown.exe
                err_msg = result.stderr.strip() or result.stdout.strip()
                messagebox.showerror(
                    "Shutdown Command Failed",
                    f"shutdown.exe returned error code {result.returncode}.\n\n"
                    f"{err_msg}\n\n"
                    "Make sure you are running as Administrator."
                )
                return False

            return True

        except FileNotFoundError:
            messagebox.showerror(
                "Error",
                "shutdown.exe not found.\n"
                "This application requires Windows."
            )
            return False

        except Exception as exc:
            messagebox.showerror("Unexpected Error", str(exc))
            return False

    def _schedule_shutdown(self, seconds: int) -> bool:
        """
        FIX: Build argument list properly — message is ONE element,
        never concatenated into a string that gets split later.

            shutdown /s /t <seconds> /c "<message>"

        Passing each token as its own list element lets Windows
        handle quoting correctly without any manual escaping.
        """
        message = (
            f"SafeShutdownTimer: {self._format_time(seconds)} remaining. "
            "Run 'shutdown /a' to cancel."
        )
        # Each argument is its own list element — NO .split() anywhere
        return self._run_shutdown([
            "/s",           # shutdown (not restart)
            "/t", str(seconds),
            "/c", message,  # message as a single element — safe
        ])

    def _cancel_shutdown(self) -> bool:
        # Simple args — still use a list for consistency
        return self._run_shutdown(["/a"])

    # ───────────────────────────────────────────────────────────
    #  BUTTON ACTIONS
    # ───────────────────────────────────────────────────────────
    def _on_schedule(self) -> None:
        if self.state == "COUNTDOWN":
            return

        if self.state == "CONFIRMING":
            if self.confirm_timer:
                self.root.after_cancel(self.confirm_timer)
                self.confirm_timer = None
            self._execute_schedule()
            return

        # Validate input
        time_str = self.time_entry.get().strip()

        if '.' in time_str:
            messagebox.showwarning(
                "Invalid Input",
                "Please enter a whole number (no decimals)."
            )
            return

        try:
            val = int(time_str)
            if val <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                "Invalid Input",
                "Enter a valid positive whole number."
            )
            return

        unit = self.unit_var.get()
        secs = val * {"sec": 1, "min": 60, "hr": 3600}[unit]

        if secs < MIN_SECS:
            messagebox.showwarning(
                "Too Short",
                f"Minimum timer is {MIN_SECS} seconds (1 minute).\n"
                "This prevents accidental immediate shutdown."
            )
            return

        if secs > MAX_SECS:
            messagebox.showwarning(
                "Too Long",
                "Maximum timer is 24 hours (86 400 seconds)."
            )
            return

        self.total_seconds     = secs
        self.remaining_seconds = secs

        if secs < CONFIRM_THRESHOLD:
            self.state = "CONFIRMING"
            self.sched_btn.config(text=" CONFIRM? ", fg=CLR_WARNING)
            self.status_label.config(
                text=">> Click SCHEDULE again to confirm.", fg=CLR_WARNING
            )
            self.countdown_label.config(text=" CONFIRM? ", fg=CLR_WARNING)
            self.confirm_timer = self.root.after(5000, self._reset_to_idle)
            return

        self._execute_schedule()

    def _execute_schedule(self) -> None:
        if not self._schedule_shutdown(self.remaining_seconds):
            self._reset_to_idle()
            return

        self.state         = "COUNTDOWN"
        self._urgent_blink = True
        self.sched_btn.config(text="  ACTIVE  ", fg=CLR_TEXT_DIM)
        self.status_label.config(
            text=">> Shutdown active. Windows will notify apps.",
            fg=CLR_SUCCESS
        )
        self.time_entry.config(state=tk.DISABLED)
        self._tick_countdown()

    def _on_cancel(self) -> None:
        if self.state == "COUNTDOWN":
            self._cancel_shutdown()
            if self.countdown_timer:
                self.root.after_cancel(self.countdown_timer)
                self.countdown_timer = None
            self.state = "CANCELLED"
            self.countdown_label.config(text=" CANCELLED ", fg=CLR_SUCCESS)
            self.status_label.config(
                text=">> Shutdown cancelled successfully.", fg=CLR_ACCENT
            )
            self._reset_to_idle_delayed()

        elif self.state == "CONFIRMING":
            if self.confirm_timer:
                self.root.after_cancel(self.confirm_timer)
                self.confirm_timer = None
            self._reset_to_idle()

    def _reset_to_idle(self) -> None:
        self.state = "IDLE"
        self.sched_btn.config(text=" SCHEDULE ", fg=CLR_TEXT)
        self.countdown_label.config(text="00:00:00", fg=CLR_TEXT_VDIM)
        self.status_label.config(
            text=">> Ready. Enter time and schedule.", fg=CLR_TEXT_DIM
        )
        self.pct_label.config(text="")
        self.progress_canvas.delete("all")
        self.time_entry.config(state=tk.NORMAL)

    def _reset_to_idle_delayed(self) -> None:
        self.time_entry.config(state=tk.NORMAL)
        self.sched_btn.config(text=" SCHEDULE ", fg=CLR_TEXT)
        if self._reset_delay_timer:
            self.root.after_cancel(self._reset_delay_timer)
        self._reset_delay_timer = self.root.after(3000, self._reset_to_idle)

    # ───────────────────────────────────────────────────────────
    #  COUNTDOWN
    # ───────────────────────────────────────────────────────────
    def _tick_countdown(self) -> None:
        if self.state != "COUNTDOWN":
            return

        self._urgent_blink = not self._urgent_blink

        color = (
            (CLR_WARNING if self._urgent_blink else CLR_ERROR)
            if self.remaining_seconds <= 10
            else CLR_TEXT
        )

        self.countdown_label.config(
            text=self._format_time(self.remaining_seconds), fg=color
        )
        self._draw_progress(
            1.0 - (self.remaining_seconds / self.total_seconds)
        )

        if self.remaining_seconds <= 0:
            self.status_label.config(text=">> Shutting down…", fg=CLR_TEXT)
            self.time_entry.config(state=tk.NORMAL)
            return

        self.remaining_seconds -= 1
        self.countdown_timer = self.root.after(1000, self._tick_countdown)

    def _draw_progress(self, progress: float) -> None:
        self.progress_canvas.delete("all")
        w, h     = 480, 22
        progress = max(0.0, min(progress, 1.0))

        if progress > 0:
            fill_w = int(w * progress)
            self.progress_canvas.create_rectangle(
                0, 0, fill_w, h,
                fill=CLR_PROGRESS_GLOW, outline=""
            )
            self.progress_canvas.create_rectangle(
                0, 2, fill_w, h - 2,
                fill=CLR_PROGRESS_FILL, outline=""
            )
            if fill_w > 3:
                self.progress_canvas.create_rectangle(
                    fill_w - 3, 0, fill_w, h,
                    fill=CLR_ACCENT, outline=""
                )

        self.pct_label.config(text=f"{int(progress * 100)}%")

    # ───────────────────────────────────────────────────────────
    #  UTILITIES
    # ───────────────────────────────────────────────────────────
    @staticmethod
    def _format_time(secs: int) -> str:
        return (
            f"{secs // 3600:02d}:"
            f"{(secs % 3600) // 60:02d}:"
            f"{secs % 60:02d}"
        )

    def _on_close(self) -> None:
        if self.confirm_timer:
            self.root.after_cancel(self.confirm_timer)
        if self._reset_delay_timer:
            self.root.after_cancel(self._reset_delay_timer)
        if self.state == "COUNTDOWN":
            if messagebox.askyesno(
                "Shutdown Active",
                "A shutdown is still scheduled!\n\n"
                "Cancel the shutdown before closing?"
            ):
                self._cancel_shutdown()
        self.root.destroy()


# ═══════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    root = tk.Tk()
    app  = ShutdownTimerApp(root)
    root.mainloop()