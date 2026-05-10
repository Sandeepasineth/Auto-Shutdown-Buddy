# 💚 Safe Auto Shutdown Timer (Windows 11)

A safe, hacker-themed auto-shutdown timer for Windows 11 with a sleek interactive GUI. 
No data loss. No forced closures. Just a clean, normal Windows shutdown.

![Python](https://img.shields.io/badge/Python-3.x-16FF00?style=flat-square&logo=python)
![Windows 11](https://img.shields.io/badge/Windows-11-000000?style=flat-square&logo=windows11)
![License](https://img.shields.io/badge/License-MIT-00FFCC?style=flat-square)

---

## ✨ Preview

┌──────────────────────────────────────────────────┐
│ 0A F3 │ SAFE SHUTDOWN TIMER_ │ B7 2E 9C │
│ 8B │ ════════════════════ │ 4F │
│ │ > TIME: [ 30 ] │ │
│ F2 │ Unit: (·)Sec (·)Min │ 7A │
│ 3E │ ( )Hour │ C0 │
│ │ [ SCHEDULE ] [CANCEL] │ │
│ 9A │ ████████████░░░░░░░░ │ 5B │
│ │ │ │
│ 4D │ 00:14:22 │ │
│ │ >> Shutdown active. │ 2A │
│ 1E │ > Safe: Apps save │ │
│ │ > Non-force guaranteed│ B9 │
└──────────────────────────────────────────────────┘


---

## 🛡️ Why is it "Safe"?

Unlike other shutdown tools, this timer guarantees your Windows files and unsaved work are protected:

- **No `/f` flag:** Identical to clicking "Shut down" in the Start menu.
- **Apps save data:** Windows sends `WM_QUERYENDSESSION` to every app, giving them time to save.
- **Clean filesystem:** Windows flushes all buffers and unmounts drives safely before power-off.
- **Survives crashes:** The timer is OS-level. If the app crashes, Windows still shuts down normally.
- **Always cancellable:** Click `CANCEL`, close the window, or run `shutdown /a` in any terminal.
- **Accident-proof:** 1-minute minimum enforced. Double-confirmation required for timers under 5 minutes.
- **Auto-Admin:** Automatically prompts for Administrator privileges (required by Windows to schedule shutdowns).

---

## 🚀 Option 1: Using the `.exe` (No Python Needed)

If you just want to use the app immediately:

1. Download the **`shutdown_timer.exe`** file from this repository.
2. Double-click `shutdown_timer.exe`.
3. Windows will show an Admin prompt (🛡️). Click **"Yes"**.
4. Set your time and click **SCHEDULE**!

> ℹ️ **Windows SmartScreen Warning:** 
> Because the `.exe` is homemade and not signed by a Microsoft certificate, Windows might show a blue popup saying *"Windows protected your PC"* the first time. 
> **To bypass it:** Click `More info` → `Run anyway`. It is 100% safe—it's literally the code in this repository!

---

## 🐍 Option 2: Running the Python Source Code

If you prefer to run the raw Python script (or want to modify it):

### Prerequisites
- [Python 3.x](https://www.python.org/downloads/) installed.
- ⚠️ Make sure you checked **"Add Python to PATH"** during installation.

### Steps
1. Clone or download this repository:
   ```bash
   git clone https://github.com/Sandeepasineth/Auto-Shutdown-Buddy.git
   cd Auto-Shutdown-Buddy
