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
from datetime import datetime

velocity = 20
vc = 30
tau = 0.1
num = 2
safe_d = 5


def getdec(v, n):
    if n != 1:
        return 4
    else:
        return 4


def get_maxacc(v):
    return 0


def getrss(V1, a, b):
    v1 = V1.get_velocity()
    v2 = v1
    t = V1.get_transform().get_forward_vector()
    v1 = velocity  # v1.x#(v1).dot(t)/np.sqrt((t).dot(t))
    v2 = velocity  # v2.x#S (v2).dot(t) / np.sqrt((t).dot(t))
    print(v1, v2)
    a2c = get_maxacc(v2)
    l1 = V1.bounding_box.extent.x * 2
    a1 = getdec(v1, a)
    a2 = getdec(v2, b)
    if a1 >= a2:
        print("uwu")
        d = (a2c / 2) * (a2c / a2 + 1) * (tau ** 2) + v2 * (a2c / a2 + 1) * tau + (
                    v2 ** 2 / (2 * a2) - v1 ** 2 / (2 * a1)) + l1 + safe_d
    else:
        if tau >= (v1 - v2) / (a2c + a1) and tau <= (v1 * a2 / a1 - v2) / (a2c + a2):
            print("--------")
            d = (v2 - v1) * tau + (tau ** 2) * (a1 + a2c) / 2 + (v1 - v2 - (a1 + a2c) * tau) ** 2 / (
                        2 * (a2 - a1)) + l1 * 2 + safe_d
        else:
            print("tgcvgtvvfyvf")
            d = a2c * (a2c / a2 + 1) * (tau ** 2) / 2 + v2 * (a2c / a2 + 1) * tau + (
                        (v2 ** 2) / (2 * a2) - (v1 ** 2) / (2 * a1)) + l1 * 2 + safe_d
    print(a, b, d)
    return d


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


class spawn:
    def __init__(self, num, V, sp,velocity):
        self.velocity = V.get_velocity()
        self.velocity.x = velocity
        self.num = num - 1
        self.V = V
        self.sp = sp
        self.list = []
        self.list.append(self.V)
        self.V.set_target_velocity(self.velocity)
        self.i = 0

    def next(self):
        if self.num > 0:
            vec = self.sp.rotation.get_forward_vector()
            rss_d = getrss(self.V, self.i, self.i + 1)
            self.sp.location = self.sp.location + carla.Location(-rss_d * vec.x / np.sqrt((vec).dot(vec)), -rss_d *
                                                                 # self.sp.location = self.sp.location + carla.Location(-rss_d , -rss_d *
                                                                 vec.y / np.sqrt((vec).dot(vec)), 1)
            follower = world.spawn_actor(bp, self.sp)
            self.V = follower
            self.V.set_target_velocity(self.velocity)
            self.list.append(self.V)
            actor_list.append(follower)
            self.i = self.i + 1
            self.num = self.num - 1
            if num > 0:
                self.next()

    def get_list(self):
        return self.list


def reset_spec(V, spectator):
    transform = V.get_transform()
    spectator.set_transform(
        carla.Transform(transform.location + carla.Location(z=200), carla.Rotation(pitch=-90)))

def move(v,a0,a1,y,velocity,t):
    t0 = datetime.now()
    t2 = t0

    vel = list[0].get_velocity()
    reset_spec(list[0], spectator)
    print(getd(list[0], list[1]), "-----------")
    while ((t2 - t0).total_seconds()) < t:
        t2 = datetime.now()
        for i in range(len(a0)):
            vel.x = velocity[i] - a0[i] * ((t2 - t0).total_seconds())
            vel.y = y[i] * ((t2 - t0).total_seconds())
            v[i].set_target_velocity(vel)


        reset_spec(list[0], spectator)
    t0 = datetime.now()
    print(vel.x)
    while ((t2 - t0).total_seconds()) < t:
        t2 = datetime.now()
        for i in range(len(a0)):
            vel.x = velocity[i] + a1[i] * ((t2 - t0).total_seconds()-a0[i])
            vel.y = -y[i] * ((t2 - t0).total_seconds())
            v[i].set_target_velocity(vel)

        reset_spec(list[0], spectator)
    print(vel.x)
    vel.x = velocity[0]
    vel.y=0
    v[0].set_target_velocity(vel)

actor_list = []
try:
    client = carla.Client('localhost', 2000)
    client.set_timeout(2.0)
    world = client.get_world()
    world = client.load_world('Town05')

    blueprint_library = world.get_blueprint_library()

    bp = blueprint_library.filter('model3')[0]
    print(bp)

    spawn_point = world.get_map().get_spawn_points()[46]
    target = world.spawn_actor(bp, spawn_point)
    actor_list.append(target)


    obj = spawn(num, target, spawn_point,velocity)
    obj.next()
    list = obj.get_list()

    spawn_point = world.get_map().get_spawn_points()[45]
    lanelead = world.spawn_actor(bp, spawn_point)
    actor_list.append(lanelead)

    obj = spawn(3, target, spawn_point, vc)
    obj.next()
    list1 = obj.get_list()
    change=list1[1]

    """spawn_point = world.get_map().get_spawn_points()[]
    change = world.spawn_actor(bp, spawn_point)
    change.set_target_velocity(vca)
    actor_list.append(change)"""

    spectator = world.get_spectator()
    actor_list.append(spectator)
    while True:

        #time.sleep(0.1)
        r1 = getrss(list[1], 0, 1) / 2
        D=list[0].get_transform().location.x-change.get_transform().location.x-r1*2
        dv=list[0].get_velocity().x-change.get_velocity().x
        dy=(list[0].get_velocity().y-change.get_velocity().y)/2
        a0=D/4+3*(dv)/4
        a1=D/4+(dv)/4

        print("---", r1 * 2)
        #move([list[1],change],[r1,a0],[r1,a1],[0,dy],[velocity,vc],2)
        move([list[1],change,list1[2]],[r1,a0,a0],[r1,a1,a1],[0,dy,0],[velocity,vc,vc],2)

        print(getd(list[0], list[1]), "-----------", list[1].get_velocity())

        time.sleep(10)



finally:
    print('destroying actors')
    for actor in actor_list:
        actor.destroy()
