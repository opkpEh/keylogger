import socket
import json
import threading
from typing import Optional, Callable


class KeyboardNetworkServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 12345):
        self.host = host
        self.port = port
        self._running = False
        self._server_socket: Optional[socket.socket] = None
        self._clients = []
        self._callback: Optional[Callable[[dict], None]] = None

    def start(self, callback: Optional[Callable[[dict], None]] = None):
        if self._running:
            return

        self._callback = callback
        self._running = True

        try:
            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._server_socket.bind((self.host, self.port))
            self._server_socket.listen(5)

            print(f"Server listening on {self.host}:{self.port}")

            accept_thread = threading.Thread(target=self._accept_connections)
            accept_thread.daemon = True
            accept_thread.start()

        except Exception as e:
            print(f"Server error: {e}")
            self.stop()

    def stop(self):
        self._running = False

        for client in self._clients:
            try:
                client.close()
            except:
                pass
        self._clients.clear()

        if self._server_socket:
            try:
                self._server_socket.close()
            except:
                pass
            self._server_socket = None

    def _accept_connections(self):
        while self._running:
            try:
                client_socket, address = self._server_socket.accept()
                print(f"New connection from {address}")

                self._clients.append(client_socket)

                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()

            except Exception as e:
                if self._running:
                    print(f"Error accepting connection: {e}")
                break

    def _handle_client(self, client_socket: socket.socket, address):
        buffer = ""

        while self._running:
            try:
                data = client_socket.recv(4096).decode()
                if not data:
                    break

                buffer += data

                while "\n" in buffer:
                    message, buffer = buffer.split("\n", 1)
                    try:
                        event_data = json.loads(message)
                        if self._callback:
                            self._callback(event_data)
                        else:
                            key = event_data["key"]
                            state = event_data["state"]
                            modifiers = "+".join(event_data["modifiers"])
                            if modifiers:
                                print(f"{modifiers}+{key} {state}")
                            else:
                                print(f"{key} {state}")
                    except json.JSONDecodeError as e:
                        print(f"Error decoding message: {e}")

            except Exception as e:
                if self._running:
                    print(f"Error handling client {address}: {e}")
                break

        if client_socket in self._clients:
            self._clients.remove(client_socket)
        try:
            client_socket.close()
        except:
            pass
        print(f"Client {address} disconnected")


if __name__ == "__main__":
    def handle_event(event_data: dict):
        key = event_data["key"]
        state = event_data["state"]
        modifiers = "+".join(event_data["modifiers"])
        if modifiers:
            print(f"{modifiers}+{key} {state}")
        else:
            print(f"{key} {state}")


    server = KeyboardNetworkServer()
    server.start(callback=handle_event)

    print("Server running (press Ctrl+C to stop)...")
    try:
        while True:
            import time

            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping server...")
        server.stop()
        print("Server stopped.")