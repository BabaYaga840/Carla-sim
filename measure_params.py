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

IM_WIDTH = 640
IM_HEIGHT = 480
initial_d = 10




class getparams:
    def __init__(self,vehicle):
        self.v0=0
        self.v1=0
        self.acc=0
        self.time0=datetime.now()
        self.time1 = datetime.now()
        self.vehicle=vehicle
        self.x0=self.vehicle.get_transform().location
        self.x1 = self.vehicle.get_transform().location
    def update(self):
        self.x1 = self.vehicle.get_transform().location
        self.time1=datetime.now()
        self.v1=getd(self.x1,self.x0)/(self.time1-self.time0)
        self.a=(self.v1-self.v0)/(self.time1-self.time0)
        self.x0=self.x1
        self.v0=self.v1
        self.time0=self.time1
        print("---v---", self.v1)
        print("---a---", self.a)

def getd(v1, v2):
    V = v1
    x1 = V.x
    y1 = V.x
    z1 = V.x
    V = v2
    x2 = V.x
    y2 = V.y
    z2 = V.z
    d = math.sqrt((x1 - x2)**2 + (y1 - y2)**2 + (z1 - z2)**2) 
    return d






actor_list = []
try:
    client = carla.Client('localhost', 2000)
    client.set_timeout(2.0)
    world = client.get_world()
    world = client.load_world('Town05')

    blueprint_library = world.get_blueprint_library()

    bp = blueprint_library.filter('model3')[0]
    print(bp)

    spawn_point = world.get_map().get_spawn_points()[190]

    target = world.spawn_actor(bp, spawn_point)
    # get current vehicle transform to get both location & rotation
    tf = spawn_point  # target.get_transform()
    actor_list.append(target)
    meas = getparams(target)
    while True:
        target.apply_control(carla.VehicleControl(throttle=0.5, steer=0))
        spectator = world.get_spectator()
        transform = target.get_transform()
        spectator.set_transform(carla.Transform(transform.location + carla.Location(z=200), carla.Rotation(pitch=-90)))
        actor_list.append(spectator)
        time.sleep(1)
        meas.update()


finally:
    print('destroying actors')
    for actor in actor_list:
        actor.destroy()
