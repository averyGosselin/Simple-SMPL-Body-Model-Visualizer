import socket
import threading
import time

from loguru import logger

from utils.smpl_straming_visualizer import SMPLStreamingVisualizer

HOST = "127.0.0.1"
PORT = 5001

viz = SMPLStreamingVisualizer(width=1280, height=720)


def _parse_angles(line: str):
    """
    Parse joints and angles from generalized format: t (time),jointKey:x:y:z[,jointKey:x:y:z...]
    Returns (t, joint_updates_dict).
    """
    parts = line.split(",")
    if len(parts) < 2:
        raise ValueError("Too few fields")

    t = float(parts[0])

    updates = {}
    for entry in parts[1:]:
        tokens = entry.split(":")
        if len(tokens) != 4:
            # Skip malformed tokens to keep the stream alive
            logger.info(f"Skipping malformed joint token: {entry!r}")
            continue
        joint_key, x_str, y_str, z_str = tokens
        try:
            updates[joint_key] = [float(x_str), float(y_str), float(z_str)]
        except ValueError:
            logger.info(f"Non-numeric angles in token: {entry!r}")
            continue

    if not updates:
        raise ValueError("No valid joint updates parsed")

    return t, updates


def main():
    # Connect to the angle-streaming server and update the SMPL visualizer
    while True:
        try:
            with socket.create_connection((HOST, PORT)) as sock:
                logger.info(f"Connected to {HOST}:{PORT}")

                # Wrap the socket in a file-like object so we can read line by line
                with sock.makefile("r", encoding="utf-8") as f:
                    try:
                        for line in f:
                            line = line.strip()
                            if not line:
                                continue

                            try:
                                t, joint_updates = _parse_angles(line)
                                viz.update_body_pose(joint_updates)
                                pretty_updates = "; ".join(
                                    f"{k}: {v}" for k, v in joint_updates.items()
                                )
                                logger.info(f"t={t:.3f}, joints=({pretty_updates})")
                            except ValueError as e:
                                logger.error(f"[visualizer]: {line} ({e})")
                    except KeyboardInterrupt:
                        logger.info("Interrupted by user; closing connection")

        except ConnectionRefusedError as e:
            logger.error(f"Connection refused: {e}; retrying in 5 seconds...")
            time.sleep(5)

        except Exception as e:
            logger.error(f"Connection error: {e}; exiting...")
            break

    logger.info("Disconnected from server")


if __name__ == "__main__":
    threading.Thread(target=main, daemon=True).start()
    viz.run()
