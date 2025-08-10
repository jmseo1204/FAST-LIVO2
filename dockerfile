FROM osrf/ros:humble-desktop

RUN apt update && apt install -y \
    ros-humble-rosbag2 \
    ros-humble-rosbag2-storage-default-plugins \
    ros-humble-rosbag2-storage-rosbag-v2 \
    ros-humble-ros1-bridge \
    python3-colcon-common-extensions \
    && rm -rf /var/lib/apt/lists/*