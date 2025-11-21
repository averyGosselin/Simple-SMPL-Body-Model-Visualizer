import threading
from utils.vis_tools import SMPLStreamingVisualizer
import time

shoulderXYZ = [0.0, 50.0, 0.0]
elbowXYZ = [0.0, 0.0, 0.0]

viz = SMPLStreamingVisualizer(width=1280, height=720)

def display_example():
    shoulderXYZ = [0.0, 0.0, 0.0]
    elbowXYZ = [0.0, 0.0, 0.0]

    for i in range(0, 3):
        for j in range(-90, 90, 5):
            shoulderXYZ[i] = j
            viz.update_body_pose(shoulder_xyz_deg=shoulderXYZ, elbow_xyz_deg=elbowXYZ)
            time.sleep(0.1)
        shoulderXYZ[i] = 0
    
    for i in range(0, 3):
        for j in range(-90, 90, 5):
            elbowXYZ[i] = j
            viz.update_body_pose(shoulder_xyz_deg=shoulderXYZ, elbow_xyz_deg=elbowXYZ)
            time.sleep(0.1)
        elbowXYZ[i] = 0

threading.Thread(target=display_example, daemon=True).start()
viz.run()  # blocks; window stays responsive while updates arrive
