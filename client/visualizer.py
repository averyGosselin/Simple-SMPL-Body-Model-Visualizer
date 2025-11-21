import socket
import threading
from utils.vis_tools import SMPLStreamingVisualizer

HOST = "127.0.0.1"
PORT = 5001

viz = SMPLStreamingVisualizer(width=1280, height=720)

def main():
    # Connect to the angle-streaming server and update the SMPL visualizer
    shoulderXYZ = [0.0, 0.0, 0.0]
    elbowXYZ = [0.0, 0.0, 0.0]

    with socket.create_connection((HOST, PORT)) as sock:
        print(f"[visualizer] Connected to {HOST}:{PORT}")

        # Wrap the socket in a file-like object so we can read line by line
        with sock.makefile("r", encoding="utf-8") as f:
            try:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    # Expecting "t,sx,sy,sz,ex,ey,ez"
                    try:
                        parts = line.split(",")
                        if len(parts) != 7:
                            raise ValueError(f"Expected 7 fields, got {len(parts)}")

                        t_str, sx_str, sy_str, sz_str, ex_str, ey_str, ez_str = parts
                        t = float(t_str)

                        shoulderXYZ[0] = float(sx_str)
                        shoulderXYZ[1] = float(sy_str)
                        shoulderXYZ[2] = float(sz_str)

                        elbowXYZ[0] = float(ex_str)
                        elbowXYZ[1] = float(ey_str)
                        elbowXYZ[2] = float(ez_str)

                        # Push the pose into the visualizer
                        viz.update_body_pose(
                            shoulder_xyz_deg=shoulderXYZ,
                            elbow_xyz_deg=elbowXYZ,
                        )

                        print(
                            f"[visualizer] t={t:.3f}, "
                            f"shoulder={shoulderXYZ}, "
                            f"elbow={elbowXYZ}"
                        )
                    except ValueError:
                        # Fallback if the line isn't in the expected format
                        print(f"[visualizer] raw: {line}")
            except KeyboardInterrupt:
                print("[visualizer] Interrupted by user; closing connection")

    print("[visualizer] Disconnected from server")

threading.Thread(target=main, daemon=True).start()
viz.run()  # blocks; window stays responsive while updates arrive
