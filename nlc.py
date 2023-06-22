import sys
import glob
import os

try:
    sys.path.append(glob.glob('../../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla
import time
import math
import numpy as np
import random
from agents.navigation.controller import VehiclePIDController

dt = 1.0 / 20.0
args_lateral_dict = {'K_P': 1.95, 'K_I': 0.05, 'K_D': 0.2, 'dt': dt}
args_longitudinal_dict = {'K_P': 1.0, 'K_I': 0.05, 'K_D': 0, 'dt': dt}
max_throt = 0.75
max_brake = 0.3
max_steer = 0.8
offset = 0
VEHICLE_VEL = 5

actorList = []
try:
    client = carla.Client("localhost", 2000)
    client.set_timeout(10.0)
    world = client.load_world("Town05")

    spectator = world.get_spectator()
    actorList.append(spectator)

    settings = world.get_settings()
    settings.synchronous_mode = True
    settings.fixed_delta_seconds = 1 / 20
    world.apply_settings(settings)

    blueprint_library = world.get_blueprint_library()
    vehicle_bp = blueprint_library.filter("cybertruck")[0]

    vehicle = None
    while (vehicle is None):
        spawn_points = world.get_map().get_spawn_points()
        spawn_point = spawn_points[126]
        vehicle = world.try_spawn_actor(vehicle_bp, spawn_point)
    actorList.append(vehicle)

    vehicle_controller = VehiclePIDController(vehicle,
                                              args_lateral=args_lateral_dict,
                                              args_longitudinal=args_longitudinal_dict,
                                              offset=offset,
                                              max_throttle=max_throt,
                                              max_brake=max_brake,
                                              max_steering=max_steer)

    old_yaw = math.radians(vehicle.get_transform().rotation.yaw)
    old_x = vehicle.get_transform().location.x
    old_y = vehicle.get_transform().location.y

spectator_transform = vehicle.get_transform()
spectator_transform.location += carla.Location(x=10, y=0, z=5.0)

control = carla.VehicleControl()
control.throttle = 1.0
vehicle.apply_control(control)

while True:


    current_waypoint = world.get_map().get_waypoint(vehicle.get_location())
    # if not turned_left :
    left_waypoint = current_waypoint.get_left_lane()
    if (left_waypoint is not None and left_waypoint.lane_type == carla.LaneType.Driving):
        target_waypoint = left_waypoint.previous(0.3)[0]
        turned_left = True
    else:
        if (turned_left):
            target_waypoint = waypoint.previous(0.3)[0]
        else:  # I tryed commenting this else section but the bug is still present so I dont suspect the bug relates to this else part
            target_waypoint = waypoint.next(0.3)[0]

    world.debug.draw_string(target_waypoint.transform.location, 'O', draw_shadow=False,
                            color=carla.Color(r=255, g=0, b=0), life_time=120.0,
                            persistent_lines=True)
    control_signal = vehicle_controller.run_step(VEHICLE_VEL, target_waypoint)

    vehicle.apply_control(control_signal)

    new_yaw = math.radians(vehicle.get_transform().rotation.yaw)
    spectator_transform = vehicle.get_transform()
    spectator_transform.location += carla.Location(x=-10 * math.cos(new_yaw), y=-10 * math.sin(new_yaw), z=5.0)

    spectator.set_transform(spectator_transform)

    world.tick()
finally:
    print("Destroying actors")
    client.apply_batch([carla.command.DestroyActor(x) for x in actorList])
