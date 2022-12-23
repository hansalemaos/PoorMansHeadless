import os
import time
import ctypes
from ctypes import wintypes as w
from ctypes import windll, WINFUNCTYPE, sizeof
from ctypes import wintypes
from ctypes.wintypes import DWORD, WORD
from math import floor
import kthread
from a_cv_imwrite_imread_plus import save_cv_image
from ctypes_window_info import get_window_infos
import pandas as pd
from ctypes_screenshots import screencapture_window
import sys
import cv2

GWL_EXSTYLE = -20
WS_EX_TOOLWINDOW = 0x00000080
fakeheadless = sys.modules[__name__]
fakeheadless.video_enabled = True
fakeheadless.save_screenshots_enabled = True

user32 = ctypes.WinDLL("user32", use_last_error=True)

user32.GetForegroundWindow.argtypes = ()
user32.GetForegroundWindow.restype = w.HWND
user32.ShowWindow.argtypes = w.HWND, w.BOOL
user32.ShowWindow.restype = w.BOOL
emptyLong = ctypes.c_ulong()


prototype = WINFUNCTYPE(
    wintypes.BOOL, wintypes.HWND, wintypes.COLORREF, wintypes.BYTE, wintypes.DWORD
)
paramflags = (1, "hwnd"), (1, "crKey"), (1, "bAlpha"), (1, "dwFlags")
SetLayeredWindowAttributes = prototype(
    ("SetLayeredWindowAttributes", windll.user32), paramflags
)
prototype = WINFUNCTYPE(
    wintypes.LONG,
    wintypes.HWND,
    ctypes.c_int,
    wintypes.LONG,
)
paramflags = (1, "hwnd"), (1, "nIndex"), (1, "dwNewLong")
SetWindowLongA = prototype(("SetWindowLongA", windll.user32), paramflags)
prototype = WINFUNCTYPE(
    wintypes.LONG,
    wintypes.HWND,
    ctypes.c_int,
)
paramflags = (1, "hwnd"), (1, "nIndex")
GetWindowLongA = prototype(("GetWindowLongA", windll.user32), paramflags)
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
LWA_ALPHA = 0x2
LWA_COLORKEY = 0x1
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_ABSOLUTE = 0x8000

MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
INPUT_MOUSE = 0
KEYEVENTF_UNICODE = 4
MAPVK_VK_TO_VSC = 0
SendMessage = ctypes.windll.user32.SendMessageW


def window_HIDE(hwnd: int):
    user32.ShowWindow(hwnd, 0)


def window_NORMAL(hwnd: int):
    user32.ShowWindow(hwnd, 1)


def window_SHOWMINIMIZED(hwnd: int):
    user32.ShowWindow(hwnd, 2)


def window_MAXIMIZE(hwnd: int):
    user32.ShowWindow(hwnd, 3)


def window_SHOWNOACTIVATE(hwnd: int):
    user32.ShowWindow(hwnd, 4)


def window_SHOW(hwnd: int):
    user32.ShowWindow(hwnd, 5)


def window_MINIMIZE(hwnd: int):
    user32.ShowWindow(hwnd, 6)


def window_SHOWMINNOACTIVE(hwnd: int):
    user32.ShowWindow(hwnd, 7)


def window_SHOWNA(hwnd: int):
    user32.ShowWindow(hwnd, 8)


def window_RESTORE(hwnd: int):
    user32.ShowWindow(hwnd, 9)


def window_SHOWDEFAULT(hwnd: int):
    user32.ShowWindow(hwnd, 10)


def window_FORCEMINIMIZE(hwnd: int):
    user32.ShowWindow(hwnd, 11)


def resize_window(hwnd: int, position: tuple):
    user32.SetProcessDPIAware()
    user32.MoveWindow(hwnd, *position, True)


def make_color_transparent(hwnd, color, value=0):
    SetWindowLongA(hwnd, GWL_EXSTYLE, GetWindowLongA(hwnd, GWL_EXSTYLE) | WS_EX_LAYERED)
    SetLayeredWindowAttributes(hwnd, wintypes.RGB(*color), value, LWA_COLORKEY)


def make_window_transparent(hwnd, value=0):
    SetWindowLongA(hwnd, GWL_EXSTYLE, GetWindowLongA(hwnd, GWL_EXSTYLE) | WS_EX_LAYERED)
    SetLayeredWindowAttributes(hwnd, wintypes.RGB(0, 0, 0), value, LWA_ALPHA)


def make_window_visible(hwnd):
    make_window_transparent(hwnd, value=255)


def activate_window(hwnd):
    SWP_NOSIZE = 1
    SWP_NOMOVE = 2
    ctypes.windll.user32.SetWindowPos(
        hwnd, ctypes.wintypes.HWND(1), 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE
    )
    ctypes.windll.user32.BringWindowToTop(hwnd)
    ctypes.windll.user32.SetWindowPos(
        hwnd, ctypes.wintypes.HWND(-2), 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE
    )

    user32.SetForegroundWindow(hwnd)
    if user32.IsIconic(hwnd):
        user32.ShowWindow(hwnd, 9)


def activate_topmost(hwnd):
    ctypes.windll.user32.BringWindowToTop(hwnd)  # works OK
    HWND_TOPMOST = -1
    SWP_NOSIZE = 1
    SWP_NOMOVE = 2
    user32.SetForegroundWindow(hwnd)
    if user32.IsIconic(hwnd):
        user32.ShowWindow(hwnd, 9)
    ctypes.windll.user32.SetWindowPos(
        hwnd, ctypes.wintypes.HWND(HWND_TOPMOST), 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE
    )


class POINT_(ctypes.Structure):
    _fields_ = [("x", ctypes.c_int), ("y", ctypes.c_int)]


def get_cursor():
    pos = POINT_()
    user32.GetCursorPos(ctypes.byref(pos))
    return pos.x, pos.y


ULONG_PTR = ctypes.c_ulong if sizeof(ctypes.c_void_p) == 4 else ctypes.c_ulonglong


class POINT_(ctypes.Structure):
    _fields_ = [("x", ctypes.c_int), ("y", ctypes.c_int)]


class CURSORINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_uint),
        ("flags", ctypes.c_uint),
        ("hCursor", ctypes.c_void_p),
        ("ptScreenPos", POINT_),
    ]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = (
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    )


class KEYBDINPUT(ctypes.Structure):
    _fields_ = (
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    )

    def __init__(self, *args, **kwds):
        super(KEYBDINPUT, self).__init__(*args, **kwds)
        if not self.dwFlags & KEYEVENTF_UNICODE:
            self.wScan = user32.MapVirtualKeyExW(self.wVk, MAPVK_VK_TO_VSC, 0)


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    )


class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = (("ki", KEYBDINPUT), ("mi", MOUSEINPUT), ("hi", HARDWAREINPUT))

    _anonymous_ = ("_input",)
    _fields_ = (("type", wintypes.DWORD), ("_input", _INPUT))


def _mouse_click(flags):
    x = INPUT(type=INPUT_MOUSE, mi=MOUSEINPUT(0, 0, 0, flags, 0, 0))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(INPUT))


def left_click(delay=0.1):
    _mouse_click(MOUSEEVENTF_LEFTDOWN)
    time.sleep(delay)
    _mouse_click(MOUSEEVENTF_LEFTUP)


def force_activate_window(hwnd):
    activate_topmost(hwnd)
    time.sleep(0.01)
    WM_SYSCOMMAND = ctypes.c_int(0x0112)
    SC_CLOSE = ctypes.c_int(0xF000)
    user32.SetForegroundWindow(hwnd)
    if user32.IsIconic(hwnd):
        user32.ShowWindow(hwnd, 9)
    t = kthread.KThread(
        target=lambda: SendMessage(hwnd, WM_SYSCOMMAND, SC_CLOSE, 0), name="baba"
    )
    t.start()
    time.sleep(0.01)
    left_click()  # move(x, y)


class MouseInput(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", DWORD),
        ("dwFlags", DWORD),
        ("time", DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]


class KeybdInput(ctypes.Structure):
    _fields_ = [
        ("wVk", WORD),
        ("wScan", WORD),
        ("dwFlags", DWORD),
        ("time", DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]


class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", DWORD), ("wParamL", WORD), ("wParamH", WORD)]


class InputList(ctypes.Union):
    _fields_ = [("mi", MouseInput), ("ki", KeybdInput), ("hi", HardwareInput)]


class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("inputList", InputList)]


def get_resolution():
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)


def move(x, y, relative=False):
    mouseFlag = MOUSEEVENTF_MOVE

    if not relative:
        mouseFlag |= MOUSEEVENTF_ABSOLUTE
        xr, yr = get_resolution()
        x = floor(x / xr * 65535)
        y = floor(y / yr * 65535)

    inputList = InputList()
    inputList.mi = MouseInput(x, y, 0, mouseFlag, 0, ctypes.pointer(emptyLong))

    windowsInput = Input(emptyLong, inputList)
    ctypes.windll.user32.SendInput(
        1, ctypes.pointer(windowsInput), ctypes.sizeof(windowsInput)
    )


def make_window_headless(hwnd, width=None, height=None,distance_from_taskbar=1):
    altx, alty = get_cursor()
    force_activate_window(hwnd)
    user32.SetProcessDPIAware()
    user32.ShowWindow(hwnd, 6)
    user32.ShowWindow(hwnd, 9)

    aw = [x for x in get_window_infos() if x.class_name == "Shell_TrayWnd"]
    startx, starty = [x.dim_client for x in get_window_infos() if x.hwnd == hwnd][
        0
    ]  # [x.dim_client for x in aw if x.class_name == "Shell_TrayWnd"][0]
    if width is None:
        width = startx
    if height is None:
        height = starty
    windowtoresizedim = [
        x.coords_client for x in aw if x.class_name == "Shell_TrayWnd"
    ][0]
    xr,yr= get_resolution()
    print(0, yr - windowtoresizedim[3]  -distance_from_taskbar, width, height,)
    user32.MoveWindow(hwnd, 0, yr - windowtoresizedim[3]  -distance_from_taskbar, width, height, True)
    activate_window(hwnd)
    move(altx, alty)
    make_window_transparent(hwnd)
    hide_from_tasklist(hwnd)


def quit_headless_mode(hwnd):
    df = pd.DataFrame(get_window_infos())
    windowtoresize = df.loc[df.hwnd == hwnd]
    resize_window(hwnd, (0, 0, *get_resolution()))
    windowtoresizedim = windowtoresize.dim_win.iloc[0]
    newcords = (0, 0, *windowtoresizedim)

    resize_window(hwnd, newcords)
    make_window_visible(hwnd)
    show_on_tasklist(hwnd)


def resize_window(hwnd: int, position: tuple):
    user32.SetProcessDPIAware()
    user32.MoveWindow(hwnd, *position, True)


def save_screenshots(
    hwnd,
    path,
    frequency=10,
):
    piggi = screencapture_window(hwnd=hwnd)
    while True:
        _ = next(piggi)
        timestamp = time.time()
        fpath = os.path.normpath(os.path.join(path, str(timestamp) + ".png"))
        save_cv_image(fpath, _)
        if not fakeheadless.save_screenshots_enabled:
            break

        time.sleep(frequency)


def stream_window(hwnd, exit_key="q", show_fps=False):
    cv2.destroyAllWindows()
    cv2.waitKey(0)
    time.sleep(2)
    last_time = None
    piggi = screencapture_window(hwnd=hwnd)
    while True:
        _ = next(piggi)
        if not fakeheadless.video_enabled:
            break
        if show_fps:
            last_time = time.time()
        cv2.imshow("", _)
        if cv2.waitKey(25) & 0xFF == ord(exit_key):
            cv2.destroyAllWindows()
            time.sleep(1)
            break
        if show_fps:
            print(f"fps: {1 / (time.time() - last_time)}", end="\r")


def hide_from_tasklist(hwnd):
    style = windll.user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE)
    style = style | WS_EX_TOOLWINDOW
    res = windll.user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, style)


def show_on_tasklist(hwnd):
    style = windll.user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE)
    style = style | WS_EX_TOOLWINDOW
    res = windll.user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, ctypes.c_long(0x00000200))


class FakeHeadless:
    def __init__(self, hwnd):
        self.t = None
        self.hwnd = hwnd
        self.vt = None

    def enable_save_screenshots(self):
        fakeheadless.save_screenshots_enabled = True
        return self

    def disable_save_screenshots(self):
        fakeheadless.save_screenshots_enabled = False
        return self

    def start_saving_screenshots(self, folder, frequency=1):
        self.enable_save_screenshots()
        if self.vt is None:
            self.vt = kthread.KThread(
                target=save_screenshots, name="sca", args=(self.hwnd, folder, frequency)
            )
        else:
            self.disable_save_screenshots()
            time.sleep(1)
            try:
                self.t.kill()
            except Exception:
                pass
            self.enable_save_screenshots()
            self.vt = kthread.KThread(
                target=save_screenshots, name="sca", args=(self.hwnd, folder, frequency)
            )
        self.vt.start()

    def enable_video_stream(self):
        fakeheadless.video_enabled = True
        return self

    def disable_video_stream(self):
        fakeheadless.video_enabled = False
        return self

    def start_video_stream(self, exit_key="q", show_fps=False):
        self.enable_video_stream()
        if self.t is None:
            self.t = kthread.KThread(
                target=stream_window, name="sca", args=(self.hwnd, exit_key, show_fps)
            )
        else:
            self.disable_video_stream()
            time.sleep(1)
            try:
                self.t.kill()
            except Exception:
                pass
            self.enable_video_stream()
            self.t = kthread.KThread(
                target=stream_window, name="sca", args=(self.hwnd, exit_key, show_fps)
            )
        self.t.start()

    def quit_headless_mode(self):
        quit_headless_mode(self.hwnd)
        return self

    def resize_window(self, position):
        resize_window(self.hwnd, position)
        return self

    def start_headless_mode(self, width=None, height=None,distance_from_taskbar=1):
        make_window_headless(self.hwnd, width=width, height=height,distance_from_taskbar=distance_from_taskbar)
        return self

    def get_resolution(self):
        return get_resolution()

    def force_activate_window(self):
        force_activate_window(self.hwnd)
        return self

    def activate_topmost(
        self,
    ):
        activate_topmost(self.hwnd)
        return self

    def activate_window(self):
        activate_window(self.hwnd)
        return self

    def make_window_visible(self):
        make_window_visible(self.hwnd)
        return self

    def hide_window(self):
        window_HIDE(self.hwnd)
        return self

    def show_window(self):
        window_SHOW(self.hwnd)
        return self

    def maximize_window(self):
        window_MAXIMIZE(self.hwnd)
        return self

    def minimize_window(self):
        window_MINIMIZE(self.hwnd)
        return self

    def minimize_window_force(self):
        window_FORCEMINIMIZE(self.hwnd)
        return self

    def restore_window(self):
        window_RESTORE(self.hwnd)
        return self

    def make_one_color_transparent(self, color):
        make_color_transparent(self.hwnd, color, value=0)
        return self

    def make_window_transparent(self):
        make_window_transparent(self.hwnd, value=0)
        return self

    def show_on_tasklist(self):
        show_on_tasklist(
            self.hwnd,
        )
        return self

    def hide_from_tasklist(self):
        hide_from_tasklist(
            self.hwnd,
        )
        return self

    @staticmethod
    def get_all_windows_with_handle():
        return get_window_infos()


