import win32api
import win32con
import time
import threading
from typing import Set, Optional, Callable


class GlobalKeyMonitor:
    def __init__(self):
        self._pressed_keys: Set[int] = set()
        self._running = False
        self._callback: Optional[Callable[[str], None]] = None
        self._thread: Optional[threading.Thread] = None

        self.KEY_NAMES = {
            win32con.VK_SHIFT: 'Shift',
            win32con.VK_CONTROL: 'Ctrl',
            win32con.VK_MENU: 'Alt',
            win32con.VK_CAPITAL: 'Caps Lock',
            win32con.VK_TAB: 'Tab',
            win32con.VK_UP: 'Up',
            win32con.VK_DOWN: 'Down',
            win32con.VK_LEFT: 'Left',
            win32con.VK_RIGHT: 'Right',
            win32con.VK_ESCAPE: 'Esc',
            win32con.VK_RETURN: 'Enter',
            win32con.VK_SPACE: 'Space',
            win32con.VK_BACK: 'Backspace',
            win32con.VK_DELETE: 'Delete',
            win32con.VK_LWIN: 'Win',
            win32con.VK_F1: 'F1',
            win32con.VK_F2: 'F2',
            win32con.VK_F3: 'F3',
            win32con.VK_F4: 'F4',
            win32con.VK_F5: 'F5',
            win32con.VK_F6: 'F6',
            win32con.VK_F7: 'F7',
            win32con.VK_F8: 'F8',
            win32con.VK_F9: 'F9',
            win32con.VK_F10: 'F10',
            win32con.VK_F11: 'F11',
            win32con.VK_F12: 'F12',
        }

        for i in range(48, 58):  # Numbers 0-9
            self.KEY_NAMES[i] = chr(i)
        for i in range(65, 91):  # Letters A-Z
            self.KEY_NAMES[i] = chr(i)

    def start(self, callback: Optional[Callable[[str], None]] = None):

        if self._running:
            return

        self._callback = callback
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join()
            self._thread = None

    def _monitor_loop(self):
        """Main monitoring loop."""
        while self._running:
            for key_code in self.KEY_NAMES:
                key_state = win32api.GetAsyncKeyState(key_code)

                is_pressed = key_state & 0x8000 != 0

                if is_pressed:
                    if key_code not in self._pressed_keys:
                        self._pressed_keys.add(key_code)
                        self._handle_key_event(key_code, True)
                else:
                    if key_code in self._pressed_keys:
                        self._pressed_keys.remove(key_code)
                        self._handle_key_event(key_code, False)

            time.sleep(0.01)

    def _handle_key_event(self, key_code: int, is_pressed: bool):
        key_name = self.KEY_NAMES.get(key_code, f'Key({key_code})')
        state = "pressed" if is_pressed else "released"

        modifiers = []
        if win32api.GetAsyncKeyState(win32con.VK_CONTROL) & 0x8000:
            modifiers.append("Ctrl")
        if win32api.GetAsyncKeyState(win32con.VK_SHIFT) & 0x8000:
            modifiers.append("Shift")
        if win32api.GetAsyncKeyState(win32con.VK_MENU) & 0x8000:
            modifiers.append("Alt")

        key_combo = "+".join(modifiers + [key_name]) if modifiers else key_name

        if self._callback:
            self._callback(f"{key_combo} {state}")

    def is_pressed(self, key_code: int) -> bool:
        return key_code in self._pressed_keys


# Example usage
if __name__ == "__main__":
    def print_key_event(key_info: str):
        print(key_info)


    monitor = GlobalKeyMonitor()
    monitor.start(callback=print_key_event)

    print("Monitoring keyboard (press Ctrl+C to exit)...")
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        monitor.stop()
        print("\nMonitoring stopped.")