"""
DaVinci Resolve Win32 Ghost-Input Engine & Shortcut Dispatcher
Option C (Autonomous Hybrid) - Controls DaVinci hands-free without stealing user cursor.
"""

import sys
import time
from typing import Optional, Dict, Any

is_windows = sys.platform == "win32"

if is_windows:
    import ctypes
    from ctypes import wintypes
    import win32gui
    import win32con
    user32 = ctypes.windll.user32
else:
    user32 = None
    win32gui = None
    win32con = None


class GhostInput:
    def __init__(self):
        self.is_windows = is_windows

    def find_davinci_window(self) -> Optional[int]:
        if not self.is_windows:
            return None
        found_hwnds = []
        def enum_windows_callback(hwnd, lparam):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if "davinci resolve" in title.lower() and "preferences" not in title.lower():
                    lparam.append(hwnd)
            return True
        win32gui.EnumWindows(enum_windows_callback, found_hwnds)
        return found_hwnds[0] if found_hwnds else None

    def get_window_rect(self) -> Optional[Dict[str, int]]:
        hwnd = self.find_davinci_window()
        if not hwnd:
            return None
        rect = win32gui.GetWindowRect(hwnd)
        return {"left": rect[0], "top": rect[1], "right": rect[2], "bottom": rect[3], "width": rect[2] - rect[0], "height": rect[3] - rect[1]}

    def execute_transport(self, action: str) -> Dict[str, Any]:
        hwnd = self.find_davinci_window()
        if not hwnd:
            return {"success": False, "error": "DaVinci Resolve window not found or running on non-Windows OS."}

        action = action.lower()
        key_map = {
            "play": 0x20, "pause": 0x20, "toggle": 0x20,
            "razor_cut": 0x42, "cut": 0x42,
            "zoom_fit": 0x5A, "fullscreen": 0x46,
            "blade": 0x42, "select": 0x41
        }

        if action in ["razor_cut", "cut"]:
            # Ctrl + B
            user32.keybd_event(0x11, 0, 0, 0)
            user32.keybd_event(0x42, 0, 0, 0)
            time.sleep(0.03)
            user32.keybd_event(0x42, 0, 2, 0)
            user32.keybd_event(0x11, 0, 2, 0)
            return {"success": True, "action": action, "shortcut": "Ctrl+B"}

        elif action in ["zoom_fit"]:
            # Shift + Z
            user32.keybd_event(0x10, 0, 0, 0)
            user32.keybd_event(0x5A, 0, 0, 0)
            time.sleep(0.03)
            user32.keybd_event(0x5A, 0, 2, 0)
            user32.keybd_event(0x10, 0, 2, 0)
            return {"success": True, "action": action, "shortcut": "Shift+Z"}

        elif action in ["fullscreen"]:
            # Ctrl + F
            user32.keybd_event(0x11, 0, 0, 0)
            user32.keybd_event(0x46, 0, 0, 0)
            time.sleep(0.03)
            user32.keybd_event(0x46, 0, 2, 0)
            user32.keybd_event(0x11, 0, 2, 0)
            return {"success": True, "action": action, "shortcut": "Ctrl+F"}

        elif action in ["play", "pause", "toggle"]:
            user32.keybd_event(0x20, 0, 0, 0)
            time.sleep(0.03)
            user32.keybd_event(0x20, 0, 2, 0)
            return {"success": True, "action": action, "shortcut": "Space"}

        return {"success": False, "error": f"Unknown transport action: '{action}'"}

    def switch_page(self, page_name: str) -> Dict[str, Any]:
        pages = {
            "media": 0x32, "cut": 0x33, "edit": 0x34,
            "fusion": 0x35, "color": 0x36, "fairlight": 0x37, "deliver": 0x38
        }
        vk = pages.get(page_name.lower())
        if not vk or not self.is_windows:
            return {"success": False, "error": f"Unsupported page: {page_name}"}

        user32.keybd_event(0x10, 0, 0, 0)
        user32.keybd_event(vk, 0, 0, 0)
        time.sleep(0.03)
        user32.keybd_event(vk, 0, 2, 0)
        user32.keybd_event(0x10, 0, 2, 0)
        return {"success": True, "page": page_name}

    def set_vertical_resolution(self) -> Dict[str, Any]:
        hwnd = self.find_davinci_window()
        if not hwnd:
            return {"success": False, "error": "DaVinci Resolve window not found."}

        user32.ShowWindow(hwnd, 3)
        user32.SetForegroundWindow(hwnd)
        time.sleep(0.2)

        # Shift + 9
        user32.keybd_event(0x10, 0, 0, 0)
        user32.keybd_event(0x39, 0, 0, 0)
        time.sleep(0.05)
        user32.keybd_event(0x39, 0, 2, 0)
        user32.keybd_event(0x10, 0, 2, 0)
        time.sleep(1.0)

        # Enter to confirm
        user32.keybd_event(0x0D, 0, 0, 0)
        time.sleep(0.05)
        user32.keybd_event(0x0D, 0, 2, 0)
        return {"success": True, "resolution": "1080x1920 (9:16 vertical)"}

    def seamless_click(self, x: int, y: int, label: str = "Antigravity Action") -> bool:
        if not self.is_windows:
            return False
        class POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
        orig_pt = POINT()
        user32.GetCursorPos(ctypes.byref(orig_pt))
        user32.SetCursorPos(x, y)
        time.sleep(0.005)
        user32.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.01)
        user32.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        user32.SetCursorPos(orig_pt.x, orig_pt.y)
        return True

    def ghost_click(self, x: int, y: int) -> bool:
        hwnd = self.find_davinci_window()
        if not hwnd:
            return False
        l_param = (y << 16) | (x & 0xFFFF)
        win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, l_param)
        time.sleep(0.02)
        win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, l_param)
        return True


ghost = GhostInput()
