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
        self.v1=getd(self.x1,self.x0)/((self.time1-self.time0).total_seconds())
        self.a=(self.v1-self.v0)/((self.time1-self.time0).total_seconds())
        self.x0=self.x1
        self.v0=self.v1
        self.time0=self.time1
        self.v1=self.vehicle.get_velocity()
        self.a=self.vehicle.get_acceleration()
        print("---v---", np.sqrt((self.v1).dot(self.v1)))
        print("---a---", np.sqrt((self.a).dot(self.a)))
        return np.sqrt((self.v1).dot(self.v1))

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
    
    
    v=target.get_velocity()
    v.x=100
    target.set_target_velocity(v)
    time1=datetime.now()
    time0=datetime.now()
    vmag=1
    while (time1-time0).total_seconds() <1:
        spectator = world.get_spectator()
        transform = target.get_transform()
        spectator.set_transform(carla.Transform(transform.location + carla.Location(z=200), carla.Rotation(pitch=-90)))
        actor_list.append(spectator)
        meas.update()
        time1=datetime.now()
    while vmag>0:
        target.apply_control(carla.VehicleControl(brake=1.0, steer=0))
        spectator = world.get_spectator()
        transform = target.get_transform()
        spectator.set_transform(carla.Transform(transform.location + carla.Location(z=200), carla.Rotation(pitch=-90)))
        actor_list.append(spectator)
        print("----------------")
        #time.sleep(1)
        vmag = meas.update()


finally:
    print('destroying actors')
    for actor in actor_list:
        actor.destroy()
