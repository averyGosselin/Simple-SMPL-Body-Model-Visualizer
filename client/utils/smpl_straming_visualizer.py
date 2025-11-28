import torch
import threading

import open3d.visualization.gui as gui
import scipy.spatial.transform.rotation as R
from loguru import logger

from utils.vis_tools import AppWindow


class SMPLStreamingVisualizer:
    """Small wrapper to run the SMPL viewer and feed poses being streamed from a server."""

    _initialized = False

    def __init__(self, width=1280, height=720):
        self.app = gui.Application.instance

        if not SMPLStreamingVisualizer._initialized:
            self.app.initialize()
            SMPLStreamingVisualizer._initialized = True

        self.window = AppWindow(width, height)
        self.body_model = "SMPL"
        self._stop_event = threading.Event()
        self._joint_index_map = self._build_joint_index_map()

    def _build_joint_index_map(self) -> dict:
        joint_index_map = {}
        joint_config = AppWindow.JOINT_NAMES.get(self.body_model, {})
        for component, names in joint_config.items():
            joint_index_map[component] = {name: idx for idx, name in enumerate(names)}
        return joint_index_map

    def _normalize_angles(self, angles, joint_key):
        if angles is None:
            logger.warning(f"Skipping joint '{joint_key}': received no angles")
            return None

        try:
            x, y, z = [float(v) for v in angles]
        except (TypeError, ValueError):
            logger.warning(
                f"Skipping joint '{joint_key}': expected three numeric angles, got {angles}"
            )
            return None

        axis_angle = R.Rotation.from_euler("xyz", [x, y, z], degrees=True).as_rotvec()
        return torch.from_numpy(axis_angle)

    def update_body_pose(
        self, joint_angles_deg: dict, component: str = "body_pose", reset: bool = True
    ):
        """
        Update one or more joints on the SMPL model.

        joint_angles_deg should be a mapping of {joint_key: [x_deg, y_deg, z_deg]}.
        component selects the pose block to edit (e.g., "body_pose", "global_orient").
            Note: component has only been tested with "body_pose
        Set reset=True to zero out the component before applying updates.
        """

        if not isinstance(joint_angles_deg, dict):
            raise TypeError("joint_angles_deg must be a dict of {joint_key: [x, y, z]}")

        if component not in AppWindow.POSE_PARAMS[self.body_model]:
            raise ValueError(
                f"Pose component '{component}' is not valid for {self.body_model}"
            )

        if component not in self._joint_index_map:
            raise ValueError(f"No joint index map found for component '{component}'")

        prepared_updates = []
        for joint_key, angles in joint_angles_deg.items():
            joint_idx = self._joint_index_map[component].get(joint_key)
            if joint_idx is None:
                logger.warning(
                    f"Unknown joint '{joint_key}' for component '{component}'"
                )
                continue

            axis_angle = self._normalize_angles(angles, joint_key)
            if axis_angle is None:
                continue

            prepared_updates.append((joint_idx, axis_angle))

        if not prepared_updates:
            logger.warning("No valid joint updates to apply; skipping pose update")
            return

        def _apply():
            pose_tensor = AppWindow.POSE_PARAMS[self.body_model][component]
            new_pose = torch.zeros_like(pose_tensor) if reset else pose_tensor.clone()

            for joint_idx, axis_angle in prepared_updates:
                new_pose[0, joint_idx] = axis_angle

            AppWindow.POSE_PARAMS[self.body_model][component] = new_pose
            self.window.load_body_model(
                self.window._body_model.selected_text,
                gender=self.window._body_model_gender.selected_text,
            )

        gui.Application.instance.post_to_main_thread(self.window.window, _apply)

    def run(self):
        """Blocking run loop; closes when window is closed."""
        self.app.run()

    def close(self):
        self.window.window.close()
