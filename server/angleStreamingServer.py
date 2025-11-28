import math
import socket
import threading
import time
from typing import Dict, Mapping, Sequence, Optional, Tuple

# NOTE: there is a demo method at the bottom of this file if you want to quickly try it


class AngleStreamingServer:
    """
    Simple TCP server that streams XYZ joint angles to a client.

    Usage (as a library):

        from server.angleStreamingServer import AngleStreamingServer
        import threading

        server = AngleStreamingServer(host="127.0.0.1", port=5001, send_interval=0.05)
        threading.Thread(target=server.serve_forever, daemon=True).start()

        # In your joint-angle generation loop:
        while True:
            joint_angles = {"right_shoulder": [sx, sy, sz], "right_elbow": [ex, ey, ez]}
            server.update_joint_angles(joint_angles)  # pushes latest angles to the viz client

    The server will continuously send lines of the form:

        t,jointKey:x:y:z,jointKey:x:y:z,...
    """

    def __init__(
        self,
        joint_keys,
        host: str = "127.0.0.1",
        port: int = 5001,
        send_interval: float = 0.05,
    ):
        self.host = host
        self.port = port
        self.send_interval = send_interval

        self._lock = threading.Lock()
        self._joint_angles: Dict[str, Sequence[float]] = {
            k: [0.0, 0.0, 0.0] for k in joint_keys
        }

        self._running = False
        self._server_sock: Optional[socket.socket] = None

    # --- API ---

    def update_joint_angles(self, joint_angles: Mapping[str, Sequence[float]]) -> None:
        """
        Update the XYZ angles that will be streamed to visualizer client.

        joint_angles should map each joint name to a list of [x, y, z] angles.
        """

        if not isinstance(joint_angles, Mapping):
            raise TypeError("joint_angles must be a mapping of joint name to [x, y, z]")

        new_payload: Dict[str, Sequence[float]] = {}
        for key in self._joint_angles.keys():
            if key not in joint_angles:
                raise ValueError(f"Missing joint '{key}' in joint_angles")
            values = joint_angles[key]
            if len(values) != 3:
                raise ValueError(f"Joint '{key}' must have exactly 3 values")
            new_payload[key] = [float(v) for v in values]

        with self._lock:
            self._joint_angles = new_payload

    def serve_forever(self) -> None:
        """
        Start listening for clients and stream the latest angles until stopped.

        This method blocks; typically you run it in a background thread. See the demo() method for an example.
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

    # --- Helpers ---

    def _snapshot_angles(self) -> Dict[str, Sequence[float]]:
        with self._lock:
            return {k: list(v) for k, v in self._joint_angles.items()}

    @staticmethod
    def _format_msg(t: float, joint_angles: Dict[str, Sequence[float]]) -> bytes:
        parts = [f"{t:.3f}"]
        for joint in joint_angles.keys():
            x, y, z = joint_angles[joint]
            parts.append(f"{joint}:{x:.4f}:{y:.4f}:{z:.4f}")
        return (",".join(parts) + "\n").encode("utf-8")

    def _handle_client(self, conn: socket.socket, addr: Tuple[str, int]) -> None:
        """Continuously send the latest angles to the connected client until it disconnects."""
        print(f"[server] Client connected from {addr}")
        try:
            with conn:
                t = 0.0
                while self._running:
                    joint_angles = self._snapshot_angles()
                    msg = self._format_msg(t, joint_angles)

                    conn.sendall(msg)
                    print(f"[server] sent to {addr}: {msg!r}")

                    t += self.send_interval
                    time.sleep(self.send_interval)

        except (BrokenPipeError, ConnectionResetError, OSError) as e:
            print(f"[server] Connection to {addr} closed: {e}")
        finally:
            print(f"[server] Client {addr} disconnected")

def demo():
    """
    Runs a demo AngleStreamingServer that does a lil dancy dance
    """
    joint_keys = [
        "right_shoulder",
        "left_shoulder",
        "spine1",
        "right_hip",
        "left_hip",
        "right_knee",
        "left_knee",
    ]
    server = AngleStreamingServer(
        joint_keys=joint_keys, host="127.0.0.1", port=5001, send_interval=0.05
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    print("[server] AngleStreamingServer started; generating demo angles...")

    start = time.time()
    try:
        while True:
            elapsed = time.time() - start
            beat = 2 * math.pi * 0.6 * elapsed  # primary tempo ~0.6 Hz

            payload = {}
            arm_swing = 35.0 * math.sin(beat)  # side-to-side
            arm_raise = 25.0 * math.sin(beat * 0.5)  # lift/lower
            payload["right_shoulder"] = [arm_swing, arm_raise, 0.0]
            payload["left_shoulder"] = [-arm_swing, -arm_raise, 0.0]

            torso_twist = 15.0 * math.sin(beat * 1.2)  # light torso twist
            payload["spine1"] = [0.0, torso_twist, 0.0]

            leg_kick = 20.0 * math.sin(beat + math.pi / 2)  # offset from arms
            payload["left_hip"] = [leg_kick, 0.0, 0.0]
            payload["right_hip"] = [-leg_kick, 0.0, 0.0]

            knee_bounce = 10.0 * math.sin(beat * 2.0)  # faster bounce for variety
            payload["left_knee"] = [knee_bounce, 0.0, 0.0]
            payload["right_knee"] = [-knee_bounce, 0.0, 0.0]

            server.update_joint_angles(payload)
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("[server] Dance angle producer interrupted")


if __name__ == "__main__":
    # When run as `python server/angleStreamingServer.py`, start a server and feed it demo angles
    demo()
