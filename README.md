<h1 align="center">
  <img
    src="https://raw.githubusercontent.com/olive-robotics/olive-ros2-interfaces/main/imgs/olive-robotics-logo-white.jpeg"
    alt="Olive Robotics"
    width="400"
  />
  <br />
  ROS 2 Interfaces
</h1>

The `olive-openrfm-fleet-adapter` repository installs the `olive-openrfm-fleet-adapter`
ROS 2 package, which offers the openrmf fleet adapter for the [ANT1](https://olive-robotics.com/products/olixbot-ant1/) robots from Olive Robotics GmbH.

## Getting Started

1. Install the fleet adapter via apt `sudo apt install ros-$ROS_DISTRO-olive-openrmf-fleet-adpater` (Supported distros: `humble`, `jazzy`)
2. Copy the config from this repo `config/config.yml`
3. Adjust necessary params in the config
e.g. fleet manager
```bash
  fleet_manager:
      prefix: "http://192.168.100.12:8000"  # Robots IP
      user: ""
      password: ""
```
4. Run the fleet adapter with following command:
```bash
ros2 launch olive_openrmf_fleet_adapter olive_fleet_adapter.launch.py nav_graph:=path_to_nav_graph.yaml config_file.=path_to_config_file
```