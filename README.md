# ROS 2 Jazzy training, phase 2

This repository contains work completed while taking [ROS 2 Jazzy: Complete
Robotics Developer Course](https://www.udemy.com/course/ros-2-jazzy-complete-robotics-developer-course/)
by Mohit Tripathi on Udemy. It is a personal learning record and is not an
official course repository.

Course content and any third-party materials remain subject to their respective
owners' rights and license terms. Attribution alone does not grant permission
to copy or redistribute course materials. No license is granted here for
third-party or course-owned content.

The perception examples use Ultralytics YOLOv8n. The model weights are not
included in this repository; Ultralytics can download `yolov8n.pt` when the
model is first loaded. The Ultralytics software and models have separate
[licensing terms](https://www.ultralytics.com/license), including AGPL-3.0 and
enterprise options. Review those terms for your intended use.

This workspace contains the phase 2 training packages. ROS build outputs,
the Python virtual environment, and downloaded third-party repositories are not
tracked. `dependencies.repos` records the revisions of the third-party source
repositories used in this workspace.

To restore the source dependencies in a fresh checkout, install `vcstool` and
run from the workspace root:

```sh
vcs import src < dependencies.repos
git -C src/moveit2_tutorials apply ../../patches/moveit2_tutorials.patch
```

The patch preserves local changes made to the MoveIt tutorials checkout. Do not
apply it a second time to an existing checkout where those changes are present.
Additional ROS and Python dependencies and local build configuration may still
be needed.