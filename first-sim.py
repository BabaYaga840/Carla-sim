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
import cv2
import math

IM_WIDTH = 640
IM_HEIGHT = 480
initial_d=20


def process_img(image):
    i = np.array(image.raw_data)
    i2 = i.reshape((IM_HEIGHT, IM_WIDTH, 4))
    i3 = i2[:, :, :3]
    cv2.imshow("", i3)
    cv2.waitKey(1)
    return i3/255.0


actor_list = []
try:
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
    tf = target.get_tranform()
    # Spawn new vehicle with some distance addition to above transformation location (say 10meter in x, y)
    (x,y,z)=tf.rotation.get_forward_vector()
    d=math.sqrt(x*x+y*y+z*z)
    tf.rotation = tf.location + carla.Location(-initial_d*x/d, -initial_d*y/d, -initial_d*z/d+10)
    follower = world.spawn_actor(bp, tf)
    #world.spawn(new_vehicle, carla.Transform(new_loc, carla.Rotation())


    actor_list.append(target)
    actor_list.append(follower)

    t_sig=get_target_signal()
    f_sig=get_follower_signal(t_sig)
    target.apply_control(carla.VehicleControl(throttle=t_sig[0][0], steer=t_sig[0][1]))
    follower.apply_control(carla.VehicleControl(throttle=f_sig[0][0], steer=f_sig[0][1]))


    time.sleep(50)

finally:
    print('destroying actors')
    for actor in actor_list:
        actor.destroy()
    print('done.')
