#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from ament_index_python import get_package_share_directory
from launch_ros.actions import Node
import os


def launch_setup(context, *args, **kwargs):
    config_file = LaunchConfiguration("config_file").perform(context)
    nav_graph = LaunchConfiguration("nav_graph").perform(context)
    server_uri = LaunchConfiguration("server_uri").perform(context)
    use_sim_time = LaunchConfiguration("use_sim_time").perform(context)
    log_level = LaunchConfiguration("log_level").perform(context)

    adapter_args = [
        "-c", config_file,
        "-n", nav_graph,
    ]

    if server_uri:
        adapter_args += ["-s", server_uri]

    if use_sim_time.lower() in ["true", "1", "yes"]:
        adapter_args += ["--use_sim_time"]

    adapter_args += ["--ros-args", "--log-level", log_level]

    return [
        Node(
            package="olive_openrmf_fleet_adapter",
            executable="fleet_adapter",
            name="olive_fleet_adapter",
            output="screen",
            arguments=adapter_args,
        )
    ]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            "config_file",
            default_value=os.path.join(get_package_share_directory("olive_openrmf_fleet_adapter"), "config", "config.yaml"),
            description="Path to Olive Open-RMF fleet adapter config.yaml",
        ),

        DeclareLaunchArgument(
            "nav_graph",
            description="Path to RMF navigation graph YAML",
        ),

        DeclareLaunchArgument(
            "server_uri",
            default_value="ws://localhost:8000/_internal",
            description="RMF Web API server internal websocket URI",
        ),

        DeclareLaunchArgument(
            "use_sim_time",
            default_value="false",
            description="Use simulation time",
        ),

        DeclareLaunchArgument(
            "log_level",
            default_value="info",
            description="ROS log level for the fleet adapter",
        ),

        OpaqueFunction(function=launch_setup),
    ])
