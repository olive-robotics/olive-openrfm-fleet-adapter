# Copyright 2021 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


'''
    The RobotAPI class is a wrapper for API calls to the robot. Here users
    are expected to fill up the implementations of functions which will be used
    by the RobotCommandHandle. For example, if your robot has a REST API, you
    will need to make http request calls to the appropriate endpoints within
    these functions.
'''
import math
import time
from typing import Optional

import requests
from requests.exceptions import RequestException

class RobotAPI:
    # The constructor below accepts parameters typically required to submit
    # http requests. Users should modify the constructor as per the
    # requirements of their robot's API
    def __init__(self, prefix: str, user: str, password: str, logger):
        self.prefix = prefix
        self.user = user
        self.password = password
        self.logger = logger
        self.connected = False

        self.timeout = 2.0
        self.last_command_id = {}
        self.last_goal_time = {}

        # Test connectivity
        connected = self.check_connection()
        if connected:
            self.logger.info("Successfully connected to the robot API server")
            self.connected = True
        else:
            self.logger.warning("Unable to connect to the robot API server")

    def _get(self, path: str) -> Optional[dict]:
        """
        Request A Get request to Robot API
        """
        try:
            response = requests.get(
                f"{self.prefix}{path}",
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
        except RequestException as exc:
            self.logger.debug(f"GET {path} failed: {exc}")
            return None

    def _post(self, path: str, payload: Optional[dict] = None) -> Optional[dict]:
        """
        Request a Post request to Robot API
        """
        try:
            response = requests.post(
                f"{self.prefix}{path}",
                json=payload or {},
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
        except RequestException as exc:
            self.logger.debug(f"POST {path} failed: {exc}")
            return None

    def check_connection(self):
        ''' Return True if connection to the robot API server is successful'''
        data = self._get("/health")
        return bool(data and data.get("ok", False))

    def position(self, robot_name: str):
        ''' Return [x, y, theta] expressed in the robot's coordinate frame or
            None if any errors are encountered'''
        data = self._get("/pose")
        if data is None:
            return None
        
        try:
            x = float(data["x"])
            y = float(data["y"])
            yaw_rad = float(data["yaw"])
            yaw_deg = math.degrees(yaw_rad)
            return [x, y, yaw_deg]
        except(KeyError, TypeError, ValueError) as exc:
            self.logger.debug(
                f"Invalid /pose response: {exc}, data={data}")
            return None

    def navigate(self, robot_name: str, pose, map_name: str):
        ''' Request the robot to navigate to pose:[x,y,theta] where x, y and
            and theta are in the robot's coordinate convention. This function
            should return True if the robot has accepted the request,
            else False'''
        if pose is None or len(pose)<3:
            return False
        
        payload={
            "map": map_name,
            "x": float(pose[0]),
            "y": float(pose[1]),
            "yaw": float(pose[2])
        }
        data = self._post("/navigate", payload)
        if data is None:
            return False
        
        accepted = bool(data.get("accepted", False))
        
        if accepted:
            self.last_command_id[robot_name] = data.get("command_id")
            self.last_goal_time[robot_name] = time.time()
        
        return accepted

    def start_process(self, robot_name: str, process: str, map_name: str):
        ''' Request the robot to begin a process. This is specific to the robot
            and the use case. For example, load/unload a cart for Deliverybot
            or begin cleaning a zone for a cleaning robot.
            Return True if the robot has accepted the request, else False'''
        
        self.logger.warning(
            f"start_process called but not implemented: {process}")
        return True

    def stop(self, robot_name: str):
        ''' Command the robot to stop.
            Return True if robot has successfully stopped. Else False'''
        data = self._post("/cancel_navigation")

        if data is None:
            return False

        return True

    def navigation_remaining_duration(self, robot_name: str):
        ''' Return the number of seconds remaining for the robot to reach its
            destination
        '''
        data = self._get("/state")
        if data is None:
            return 5.0

        status = data.get("navigation_status")
        if status in ["arrived", "idle", "cancelled"]:
            return 0.0

        eta = data.get("estimated_time_remaining")
        if eta is not None:
            try:
                return max(0.0, float(eta))
            except (TypeError, ValueError):
                pass
        return 5.0

    def navigation_completed(self, robot_name: str):
        ''' Return True if the robot has successfully completed its previous
            navigation request. Else False.'''
        data = self._get("/state")
        
        if data is None:
            return False
        
        status = data.get("navigation_status")
        current_command_id = data.get("current_command_id")
        last_command_id = self.last_command_id.get(robot_name)

        if status == "arrived":
            if self.last_command_id is None:
                return True
            return current_command_id == last_command_id

        return False

    def process_completed(self, robot_name: str):
        ''' Return True if the robot has successfully completed its previous
            process request. Else False.'''
        # ------------------------ #
        # IMPLEMENT YOUR CODE HERE #
        # ------------------------ #
        return True

    def battery_soc(self, robot_name: str):
        ''' Return the state of charge of the robot as a value between 0.0
            and 1.0. Else return None if any errors are encountered
            TODO: Implement Battery Status reader
        '''

        data = self._get("/state")
        if data is None:
            return 1.0
        
        battery = data.get("battery")
        if battery is None:
            return 1.0
            
        try: 
            return max(0.0, min(1.0, (float(battery)/100.0)))
        except (TypeError, ValueError):
            return 1.0
