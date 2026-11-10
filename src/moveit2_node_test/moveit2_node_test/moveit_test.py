"""Tutorial-style one-shot node that sends a pose target through MoveIt2."""

import rclpy
from rclpy.node import Node

from pymoveit2 import MoveIt2
from pymoveit2.robots import panda


def main() -> None:
    rclpy.init()
    node = Node("ik_node")

    try:
        moveit2 = MoveIt2(
            node=node,
            joint_names=panda.joint_names(),
            base_link_name=panda.base_link_name(),
            end_effector_name=panda.end_effector_name(),
            group_name=panda.MOVE_GROUP_ARM,
        )
        moveit2.move_to_pose(position=[0.4, 0.2, 0.5], quat_xyzw=[0.0, 0.0, 0.0, 1.0])
        moveit2.wait_until_executed()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

