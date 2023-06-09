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
initial_d = 10
tau=1

def getdec(v):
    return 5

def getrss(V1,V2):
    v1=V1.get_velocity()
    v2=V2.get_velocity()
    t=V2.get_transform().get_forward_vector()
    v1=(v1).dot(t)/np.sqrt((t).dot(t))
    v2 = (v2).dot(t) / np.sqrt((t).dot(t))
    a2c=V2.get_acceleration()
    l1=V1.bounding_box.extent.x
    l2=V2.bounding_box.extent.x
    a1=getdec(v1)
    a2=getdec(v2)
    if a1>=a2:
        return (a2c/2)*(a2c/a2+1)*(tau**2)+v2*(a2c/a2+1)*tau+(v2**2/(2*a2)-v1**2(2*a1))+l1+l2
    else:
        if tau>=(v1-v2)/(a2c+a1) and tau<=(v1*a2/a1-v2)/(a2c+a2):
            return (v2-v1)*tau+(tau**2)*(a1+a2c)/2+(v1-v2-(a1+a2c)*tau)**2/(2*(a2-a1))+l1+l2
        else:
            return a2c*(a2c/a2+1)*(tau**2)/2+v2*(a2c/a2+1)*tau+((v2**2)/(2*a2)-(v1**2)/(2*a1))+l1+l2



def getd(v1, v2):
    tf = v1.get_transform()
    V = tf.get_forward_vector()
    xf = V.x
    yf = V.y
    zf = V.z
    V = tf.location
    x1 = V.x * xf
    y1 = V.y * yf
    z1 = V.z * zf
    tf = v2.get_transform()
    V = tf.location
    x2 = V.x * xf
    y2 = V.y * yf
    z2 = V.z * zf
    d = ((x1 - x2) + (y1 - y2) + (z1 - z2)) / math.sqrt(xf ** 2 + yf ** 2 + zf ** 2)
    return d


class PID:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.kd = kd
        self.ki = ki
        self.p = 0
        self.i = 0
        self.d = 0

    def update(self, d, t):
        e = d - t
        self.d = e - self.p
        self.p = e
        self.i = self.i + e

    def move(self, v):
        th = self.kp * self.p + self.ki * self.i + self.kd * self.d
        print("--------------------", th)
        if th > 1:
            v.apply_control(carla.VehicleControl(throttle=1, steer=0))
        elif th > 0:
            v.apply_control(carla.VehicleControl(throttle=th, steer=0))
        elif th > -1:
            v.apply_control(carla.VehicleControl(brake=-th, steer=0))
        else:
            v.apply_control(carla.VehicleControl(brake=1, steer=0))


def get_target_signal():
    a = np.zeros((2, 2))
    a[0][0] = 0.1
    return a


def get_follower_signal(t_sig):
    return t_sig


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
    # Spawn new vehicle with some distance addition to above transformation location (say 10meter in x, y)
    V = tf.rotation.get_forward_vector()
    x = V.x
    y = V.y
    z = V.z
    d = math.sqrt(x * x + y * y + z * z)
    tf.location = tf.location + carla.Location(-initial_d * x / d, -initial_d * y / d, 1)
    follower = world.spawn_actor(bp, tf)
    # world.spawn(new_vehicle, carla.Transform(new_loc, carla.Rotation())
    # target.set_autopilot(True)
    # follower.set_autopilot(True)
    actor_list.append(target)
    actor_list.append(follower)
    # follower.apply_control(carla.VehicleControl(throttle=0.5, steer=0))

    con = PID(0.1, 0, 0.01)
    while True:
        target.apply_control(carla.VehicleControl(throttle=0.5, steer=0))
        spectator = world.get_spectator()
        transform = follower.get_transform()
        spectator.set_transform(carla.Transform(transform.location + carla.Location(z=200), carla.Rotation(pitch=-90)))
        actor_list.append(spectator)
        time.sleep(1)
        d = getd(target, follower)
        rss = getrss(target,follower)  # getrss(target.forward_speed,follower.forward_speed,)
        con.update(d, rss)
        con.move(follower)
        print(d)

finally:
    print('destroying actors')
    for actor in actor_list:
        actor.destroy()
