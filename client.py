import win32api
import win32con
import threading
import time
import socket
import json
from typing import Set, Optional


class KeyboardNetworkClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self._pressed_keys: Set[int] = set()
        self._running = False
        self._socket: Optional[socket.socket] = None
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
        }

        for i in range(48, 58):
            self.KEY_NAMES[i] = chr(i)
        for i in range(65, 91):
            self.KEY_NAMES[i] = chr(i)

    def connect(self):
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.connect((self.host, self.port))
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def start(self):
        if self._running:
            return

        if not self._socket and not self.connect():
            return

        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join()
            self._thread = None

        if self._socket:
            try:
                self._socket.close()
            except:
                pass
            self._socket = None

    def _monitor_loop(self):
        while self._running:
            try:
                for key_code in self.KEY_NAMES:
                    key_state = win32api.GetAsyncKeyState(key_code)
                    is_pressed = key_state & 0x8000 != 0

                    if is_pressed:
                        if key_code not in self._pressed_keys:
                            self._pressed_keys.add(key_code)
                            self._send_key_event(key_code, True)
                    else:
                        if key_code in self._pressed_keys:
                            self._pressed_keys.remove(key_code)
                            self._send_key_event(key_code, False)

                time.sleep(0.01)

            except Exception as e:
                print(f"Error in monitor loop: {e}")
                break

        self.stop()

    def _send_key_event(self, key_code: int, is_pressed: bool):
        if not self._socket:
            return

        try:
            key_name = self.KEY_NAMES.get(key_code, f'Key({key_code})')
            state = "pressed" if is_pressed else "released"

            # Get modifier keys state
            modifiers = []
            if win32api.GetAsyncKeyState(win32con.VK_CONTROL) & 0x8000:
                modifiers.append("Ctrl")
            if win32api.GetAsyncKeyState(win32con.VK_SHIFT) & 0x8000:
                modifiers.append("Shift")
            if win32api.GetAsyncKeyState(win32con.VK_MENU) & 0x8000:
                modifiers.append("Alt")

            event_data = {
                "key": key_name,
                "state": state,
                "modifiers": modifiers,
                "timestamp": time.time()
            }

            data = json.dumps(event_data) + "\n"
            self._socket.sendall(data.encode())

        except Exception as e:
            print(f"Error sending data: {e}")
            self.stop()


if __name__ == "__main__":
    SERVER_IP = "127.0.0.1"
    SERVER_PORT = 8080
    client = KeyboardNetworkClient(SERVER_IP, SERVER_PORT)

    print(f"Connecting to {SERVER_IP}:{SERVER_PORT}...")
    if client.connect():
        print("Connected! Starting keyboard monitoring...")
        client.start()

        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            client.stop()
            print("Stopped.")