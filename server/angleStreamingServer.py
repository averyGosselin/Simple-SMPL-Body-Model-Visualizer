import random
import socket
import threading
import time
from typing import Tuple, Sequence, Optional

# NOTE: there is a demo method at the bottom of this file if you want to quickly try it

class AngleStreamingServer:
    """
    !!!!!! README
    Simple TCP server that streams shoulder/elbow XYZ joint angles to a client.

    Usage (as a library):

        from server.main import AngleStreamingServer
        import threading

        server = AngleStreamingServer(host="127.0.0.1", port=5001, send_interval=0.05)
        threading.Thread(target=server.serve_forever, daemon=True).start()

        # In your joint-angle generation loop:
        while True:
            shoulder_angles = [sx, sy, sz]
            elbow_angles = [ex, ey, ez]
            server.update_angles(shoulder, elbow) -> this pushes the latest angles to the viz client

    The server will continuously send lines of the form:

        t,sx,sy,sz,ex,ey,ez
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 5001, send_interval: float = 0.05):
        self.host = host

        self.port = port
        self.send_interval = send_interval

        self._lock = threading.Lock()
        self._shoulder = [0.0, 0.0, 0.0]
        self._elbow = [0.0, 0.0, 0.0]

        self._running = False
        self._server_sock: Optional[socket.socket] = None

    # --- Public API ---

    def update_angles(self, shoulder_xyz: Sequence[float], elbow_xyz: Sequence[float]) -> None:
        """
        Update the shoulder/elbow XYZ angles that will be streamed to clients.

        Both sequences must have length 3.
        """
        if len(shoulder_xyz) != 3 or len(elbow_xyz) != 3:
            raise ValueError("shoulder_xyz and elbow_xyz must each have length 3")

        with self._lock:
            self._shoulder = [float(v) for v in shoulder_xyz]
            self._elbow = [float(v) for v in elbow_xyz]

    def serve_forever(self) -> None:
        """
        Start listening for clients and stream the latest angles until stopped.

        This method blocks; typically you run it in a background thread.
        """
        self._running = True

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            self._server_sock = s
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen()
            print(f"[server] Listening on {self.host}:{self.port}")

            while self._running:
                try:
                    conn, addr = s.accept()
                except OSError:
                    # Socket closed during stop()
                    break

                thread = threading.Thread(
                    target=self._handle_client,
                    args=(conn, addr),
                    daemon=True,
                )
                thread.start()

        print("[server] Server stopped")

    def stop(self) -> None:
        """Stop accepting new clients and stop streaming."""
        self._running = False
        if self._server_sock is not None:
            try:
                self._server_sock.close()
            except OSError:
                pass

    # --- Internal helpers ---

    def _snapshot_angles(self) -> Tuple[Sequence[float], Sequence[float]]:
        with self._lock:
            return list(self._shoulder), list(self._elbow)

    @staticmethod
    def _format_msg(t: float, shoulder_xyz: Sequence[float], elbow_xyz: Sequence[float]) -> bytes:
        sx, sy, sz = shoulder_xyz
        ex, ey, ez = elbow_xyz
        return f"{t:.3f},{sx:.4f},{sy:.4f},{sz:.4f},{ex:.4f},{ey:.4f},{ez:.4f}\n".encode("utf-8")

    def _handle_client(self, conn: socket.socket, addr: Tuple[str, int]) -> None:
        """Continuously send the latest angles to the connected client until it disconnects."""
        print(f"[server] Client connected from {addr}")
        try:
            with conn:
                t = 0.0
                while self._running:
                    shoulder, elbow = self._snapshot_angles()
                    msg = self._format_msg(t, shoulder, elbow)

                    conn.sendall(msg)
                    print(f"[server] sent to {addr}: {msg!r}")

                    t += self.send_interval
                    time.sleep(self.send_interval)

        except (BrokenPipeError, ConnectionResetError, OSError) as e:
            print(f"[server] Connection to {addr} closed: {e}")
        finally:
            print(f"[server] Client {addr} disconnected")


# --- Demo usage when run as a script ---
def _random_angle_producer(server: AngleStreamingServer, update_interval: float = .01) -> None:
    """
    Demo producer: generates random angles and pushes them into the server.

    This is only used when running this file directly, not when importing.
    """
    try:
        val = 0
        toadd = 5
        while True:
            # shoulder = [random.uniform(-45.0, 45.0) for _ in range(3)]
            shoulder = [0,0,0]
            
            if val >= 90:
                toadd *= -1

            val += toadd
            # elbow = [random.uniform(-90.0, 0.0) for _ in range(3)]
            elbow = [0,val,0]
            server.update_angles(shoulder, elbow)
            time.sleep(update_interval)
    except KeyboardInterrupt:
        print("[server] Random angle producer interrupted")


def demo():
    # When run as `python server/main.py`, start a server and feed it random angles
    server = AngleStreamingServer(host="127.0.0.1", port=5001, send_interval=0.05)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    print("[server] AngleStreamingServer started; generating random demo angles...")
    _random_angle_producer(server)

demo()