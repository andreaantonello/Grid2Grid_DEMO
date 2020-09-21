from evasdk import Eva
from evaUtilities import EvaGrids
from config.config_manager import load_use_case_config


if __name__ == "__main__":
    # Load use-case parameters
    config = load_use_case_config()

    # Connection to robot
    host = config['EVA']['comm']['host']
    token = config['EVA']['comm']['token']
    eva = Eva(host, token)

    # Compute grid points and robot joints
    eva_box = EvaGrids(eva, config, show_plot=True)
    joints = eva_box.get_grid_points(config['grids']['names'])

    # Go home before starting
    with eva.lock():
        eva.control_go_to(config['EVA']['home'])

    while True:
        for counter in range(len(joints[(config['grids']['names'][0])]['pick'])):
            joints_home = config['EVA']['home']
            joints_pick = joints[config['grids']['names'][0]]['pick'][counter]
            joints_drop = joints[config['grids']['names'][1]]['pick'][counter]
            joints_pick_hover = joints[config['grids']['names'][0]]['hover'][counter]
            joints_drop_hover = joints[config['grids']['names'][1]]['hover'][counter]

            # USER DEFINED WAY-POINTS
            joints_operation_A = [1.0819689, -0.38178113, -1.4469715, 0.0018216578, -0.9544528, -0.45301753]   # near drop-off
            joints_operation_B = [1.1585743, -0.87851846, -0.90641856, 0.0013422741, -1.3712289, 1.1612589]  # above drop-off
            joints_operation_C = [1.1583827, -0.894434, -0.94083834, 0.001054644, -1.3176339, 1.1613548]  # drop-off

            tool_path_grid_to_grid = {
                "metadata": {
                    "version": 2,
                    "default_max_speed": 0.2,
                    "next_label_id": 9,
                    "payload": config['EVA']['end_effector']['payload'],
                    "analog_modes": {"i0": "voltage", "i1": "voltage", "o0": "voltage", "o1": "voltage"}
                    },
                "waypoints": [
                    {"label_id": 1, "joints": joints_home},
                    {"label_id": 2, "joints": joints_pick_hover},
                    {"label_id": 3, "joints": joints_pick},
                    {"label_id": 4, "joints": joints_operation_A},
                    {"label_id": 5, "joints": joints_drop_hover},
                    {"label_id": 6, "joints": joints_drop},
                    {"label_id": 7, "joints": joints_operation_B},
                    {"label_id": 8, "joints": joints_operation_C},
                ],
                "timeline": [
                    {"type": "home", "waypoint_id": 0},
                    # Pick up part
                    {"type": "trajectory", "trajectory": "linear", "waypoint_id": 1},
                    {"type": "output-set", "io": {"location": "base", "type": "digital", "index": 1}, "value": True},
                    {"type": "trajectory", "trajectory": "linear", "time": 4, "waypoint_id": 2},
                    {"type": "wait", "condition": {"type": "time", "duration": 0.5}},
                    {"type": "trajectory", "trajectory": "joint_space", "waypoint_id": 1},

                    # Verify that part has been picked up and wait. If pickup not successful, trigger alarm
                    {"type": "if", "branches": [
                        {"condition": {
                            "type": "input", "io": {"location": "base", "type": "digital", "index": 2}, "value": 1,
                            "operator": "equal"
                        }, "timeline": [
                            {"type": "output-set", "io": {"location": "base", "type": "digital", "index": 3},
                             "value": True},  # Trigger alarm
                            {"type": "wait",
                             "condition": {"type": "input", "io": {"location": "base", "type": "digital", "index": 2},
                                           "value": False}},  # Wait for alarm reset
                            {"type": "output-set", "io": {"location": "base", "type": "digital", "index": 3},
                             "value": False},  # Stop alarm
                        ]},
                    ]},

                    # Move to chuck
                    {"type": "trajectory", "trajectory": "joint_space", "waypoint_id": 0},
                    {"type": "trajectory", "trajectory": "joint_space", "waypoint_id": 3},
                    {"type": "trajectory", "trajectory": "joint_space", "waypoint_id": 6},
                    {"type": "trajectory", "trajectory": "linear", "waypoint_id": 7},

                    # Drop down part to chuck
                    {"type": "output-set", "io": {"location": "base", "type": "digital", "index": 1}, "value": False},
                    {"type": "wait", "condition": {"type": "time", "duration": 0.5}},
                    {"type": "trajectory", "trajectory": "linear", "waypoint_id": 6},
                    {"type": "trajectory", "trajectory": "joint_space", "waypoint_id": 3},
                    {"type": "trajectory", "trajectory": "joint_space", "waypoint_id": 0},

                    # Start operation
                    {"type": "output-set", "io": {"location": "base", "type": "digital", "index": 0}, "value": False},

                    # Wait for input to confirm that operation has been performed
                    {"type": "wait", "condition": {"type": "input", "io": {"location": "base", "type": "digital", "index": 0}, "value": True}},  # Wait for alarm reset

                    {"type": "trajectory", "trajectory": "joint_space", "waypoint_id": 3},
                    {"type": "trajectory", "trajectory": "joint_space", "waypoint_id": 6},
                    {"type": "trajectory", "trajectory": "linear", "waypoint_id": 7},
                    {"type": "output-set", "io": {"location": "base", "type": "digital", "index": 1}, "value": True},
                    {"type": "wait", "condition": {"type": "time", "duration": 0.5}},
                    {"type": "trajectory", "trajectory": "linear", "waypoint_id": 6},

                    # Verify that part has been picked up and wait. If pickup not successful, trigger alarm
                    {"type": "if", "branches": [
                        {"condition": {
                            "type": "input", "io": {"location": "base", "type": "digital", "index": 2}, "value": 1,
                            "operator": "equal"
                        }, "timeline": [
                            {"type": "output-set", "io": {"location": "base", "type": "digital", "index": 3},
                             "value": True},  # Trigger alarm
                            {"type": "wait",
                             "condition": {"type": "input", "io": {"location": "base", "type": "digital", "index": 2},
                                           "value": False}},  # Wait for alarm reset
                            {"type": "output-set", "io": {"location": "base", "type": "digital", "index": 3},
                             "value": False},  # Stop alarm
                        ]},
                    ]},

                    # Move to drop-off tray
                    {"type": "trajectory", "trajectory": "joint_space", "waypoint_id": 3},
                    {"type": "trajectory", "trajectory": "joint_space", "waypoint_id": 0},
                    {"type": "trajectory", "trajectory": "joint_space", "waypoint_id": 4},
                    {"type": "trajectory", "trajectory": "linear", "waypoint_id": 5},
                    # Release part to drop-off tray
                    {"type": "output-set", "io": {"location": "base", "type": "digital", "index": 0}, "value": False},
                    {"type": "trajectory", "trajectory": "joint_space", "waypoint_id": 4},
                    {"type": "trajectory", "trajectory": "joint_space", "waypoint_id": 0},
                ]
            }

            with eva.lock():
                eva.control_wait_for_ready()
                eva.toolpaths_use(tool_path_grid_to_grid)
                eva.control_run(loop=1, mode="automatic")
