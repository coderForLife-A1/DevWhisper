"""Detection of running Zoom meetings and Google Meet sessions."""
from typing import List, Dict, Any
import psutil

try:
    import win32gui
    import win32process
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False


def get_active_meetings() -> List[Dict[str, Any]]:
    """Scan top-level visible windows to detect running Zoom or Google Meet sessions."""
    if not HAS_WIN32:
        return []

    meetings = []

    def enum_windows_callback(hwnd, extra):
        if not win32gui.IsWindowVisible(hwnd):
            return
        
        window_title = win32gui.GetWindowText(hwnd).strip()
        if not window_title:
            return

        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            proc = psutil.Process(pid)
            pname = proc.name().lower()

            # Zoom desktop client check
            if "zoom" in pname or ("zoom meeting" in window_title.lower()):
                meetings.append({
                    "type": "Zoom",
                    "title": window_title,
                    "pid": pid,
                    "process": pname,
                })
            # Google Meet runs inside popular web browsers
            elif pname in ["chrome.exe", "msedge.exe", "brave.exe", "firefox.exe"]:
                lower_title = window_title.lower()
                if "meet.google.com" in lower_title or "meet -" in lower_title or "google meet" in lower_title:
                    meetings.append({
                        "type": "Google Meet",
                        "title": window_title,
                        "pid": pid,
                        "process": pname,
                    })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    win32gui.EnumWindows(enum_windows_callback, None)
    
    # Deduplicate by title
    seen = set()
    unique = []
    for m in meetings:
        if m["title"] not in seen:
            seen.add(m["title"])
            unique.append(m)
    return unique

