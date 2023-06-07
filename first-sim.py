import glob
import os
import sys
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
initial_d=10


def getd(v1,v2):
    tf = v1.get_transform()
    V = tf.get_forward_vector()
    xf=V.x
    yf=V.y
    zf=V.z
    V=tf.location
    x1=V.x*xf
    y1=V.y*yf
    z1=V.z*zf
    tf = v2.get_transform()
    V=tf.location
    x2=V.x*xf
    y2=V.y*yf
    z2=V.z*zf
    d=((x1-x2)+(y1-y2)+(z1-z2))/math.sqrt(xf**2+yf**2+zf**2)
    return 2


def get_target_signal():
	a=np.zeros((2,2))
	a[0][0]=0.1
	return a

def get_follower_signal(t_sig):
	return t_sig


actor_list = []
try:
  while True:
    client = carla.Client('localhost', 2000)
    client.set_timeout(2.0)

    world = client.get_world()

    blueprint_library = world.get_blueprint_library()

    bp = blueprint_library.filter('model3')[0]
    print(bp)

    spawn_point = random.choice(world.get_map().get_spawn_points())

    target = world.spawn_actor(bp, spawn_point)

    # vehicle.set_autopilot(True)  # if you just wanted some NPCs to drive.

    # get current vehicle transform to get both location & rotation
    tf = target.get_transform()
    # Spawn new vehicle with some distance addition to above transformation location (say 10meter in x, y)
    V=tf.rotation.get_forward_vector()
    x=V.x
    y=V.y
    z=V.z
    d=math.sqrt(x*x+y*y+z*z)
    tf.location = tf.location + carla.Location(-initial_d*x/d, -initial_d*y/d, 10)   
    follower = world.spawn_actor(bp, tf)
    #world.spawn(new_vehicle, carla.Transform(new_loc, carla.Rotation())


    actor_list.append(target)
    actor_list.append(follower)
    
    spectator=world.get_spectator()
    transform=follower.get_transform()
    spectator.set_transform(carla.Transform(transform.location+carla.Location(z=50),carla.Rotation(pitch=-90)))
    actor_list.append(spectator)
    time.sleep(50)
    d=getd(target,follower)
    print(d)

    time.sleep(50)

finally:
    print('destroying actors')
    for actor in actor_list:
        actor.destroy()
    print('done.')
