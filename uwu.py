import glob
import os
import sys
from datetime import datetime

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass
import carla

import random
import time
import numpy as np
import math



actor_list = []
try:
    client = carla.Client('localhost', 2000)
    client.set_timeout(2.0)
    world = client.get_world()
    world = client.load_world('Town05')

    blueprint_library = world.get_blueprint_library()

    bp = blueprint_library.filter('model3')[0]
    print(bp)

    spawn_point = world.get_map().get_spawn_points()[129]

    target = world.spawn_actor(bp, spawn_point)

    spectator = world.get_spectator()
    transform = target.get_transform()
    spectator.set_transform(carla.Transform(transform.location + carla.Location(z=200), carla.Rotation(pitch=-90)))
    actor_list.append(spectator)

    velocity=target.get_velocity()
    velocity.x=20
    target.set_target_velocity(velocity)
    spawn_point = world.get_map().get_spawn_points()[130]

    lane = world.spawn_actor(bp, spawn_point)
    velocity.x = 0
    target.set_target_velocity(velocity)

    target.apply_control(carla.VehicleControl(throttle=0, steer=0.5))
    y=target.get_velocity().y-lane.get_velocity().y
    time.sleep(0.01)
    if target.get_velocity().y-lane.get_velocity().y>y:
        target.apply_control(carla.VehicleControl(throttle=0, steer=-0.5))
    
    while target.get_velocity().y - lane.get_velocity().y > 0:
        target.apply_control(carla.VehicleControl(throttle=0, steer=0.5))
        time.sleep(0.01)
    target.apply_control(carla.VehicleControl(throttle=0, steer=0))

finally:
    print('destroying actors')
    for actor in actor_list:
        actor.destroy()
