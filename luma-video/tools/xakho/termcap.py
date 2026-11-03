"""Quay cửa sổ Windows Terminal đang chạy Claude Code thật (cho video Claude A).
  python tools/xakho/termcap.py launch <thư_mục> "<câu lệnh cho claude>"   → mở WT mới, in hwnd
  python tools/xakho/termcap.py grab <hwnd> <out_dir> <giây> [chu_kỳ]      → chụp cửa sổ định kỳ ra PNG
  python tools/xakho/termcap.py key <hwnd> enter|down                       → gửi phím (trả lời hộp thoại tin cậy thư mục)"""
import ctypes, os, subprocess, sys, time
import win32api, win32con, win32gui
from PIL import ImageGrab

ctypes.windll.shcore.SetProcessDpiAwareness(2)


def wt_windows():
    out = []
    win32gui.EnumWindows(lambda h, _: out.append(h) if win32gui.GetClassName(h) == 'CASCADIA_HOSTING_WINDOW_CLASS' else None, None)
    return out


cmd = sys.argv[1]
if cmd == 'launch':
    folder, prompt = sys.argv[2], sys.argv[3]
    before = set(wt_windows())
    subprocess.Popen(['wt.exe', '-w', 'new', '--size', '118,34', '--pos', '40,40', '-d', folder,
                      'cmd', '/k', 'claude', '--permission-mode', 'acceptEdits', prompt])
    for _ in range(40):
        time.sleep(0.5)
        new = [h for h in wt_windows() if h not in before]
        if new:
            print(new[0]); break
elif cmd == 'grab':
    hwnd, out, secs = int(sys.argv[2]), sys.argv[3], float(sys.argv[4])
    every = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0
    os.makedirs(out, exist_ok=True)
    t0 = time.time(); i = 0
    while time.time() - t0 < secs:
        try:
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        except Exception:
            pass
        ImageGrab.grab(win32gui.GetWindowRect(hwnd), all_screens=True).save(os.path.join(out, f'f{i:03d}.png'))
        i += 1
        time.sleep(max(0, t0 + i * every - time.time()))
    win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
    print('frames', i)
elif cmd == 'key':
    hwnd, k = int(sys.argv[2]), sys.argv[3]
    win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)                 # Windows chỉ cho focus khi vừa có phím
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_SHOW); win32gui.SetForegroundWindow(hwnd)
    finally:                                                         # luôn nhả Alt (29/10: Alt bị kẹt làm liệt bàn phím)
        win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.3)
    vk = {'enter': win32con.VK_RETURN, 'down': win32con.VK_DOWN}[k]
    win32api.keybd_event(vk, 0, 0, 0); win32api.keybd_event(vk, 0, win32con.KEYEVENTF_KEYUP, 0)
