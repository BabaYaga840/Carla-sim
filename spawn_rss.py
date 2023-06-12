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

velocity=20
tau=1.0
num=4
safe_d=10

def getdec(v,n):
    if n!=1:
         return 20
    else:
         return 4

def get_maxacc(v):
    return 0

def getrss(V1,a,b):
    v1=V1.get_velocity()
    v2=v1
    t=V1.get_transform().get_forward_vector()
    v1=velocity#v1.x#(v1).dot(t)/np.sqrt((t).dot(t))
    v2 =velocity#v2.x#S (v2).dot(t) / np.sqrt((t).dot(t)) 
    print(v1,v2)
    a2c=get_maxacc(v2)
    l1=V1.bounding_box.extent.x*2
    a1=getdec(v1,a)
    a2=getdec(v2,b)
    if a1>=a2:
        print("uwu")
        d= (a2c/2)*(a2c/a2+1)*(tau**2)+v2*(a2c/a2+1)*tau+(v2**2/(2*a2)-v1**2/(2*a1))+l1+safe_d
    else:
        if tau>=(v1-v2)/(a2c+a1) and tau<=(v1*a2/a1-v2)/(a2c+a2):
            print("--------")
            d= (v2-v1)*tau+(tau**2)*(a1+a2c)/2+(v1-v2-(a1+a2c)*tau)**2/(2*(a2-a1))+l1*2+safe_d
        else:
            print("tgcvgtvvfyvf")
            d= a2c*(a2c/a2+1)*(tau**2)/2+v2*(a2c/a2+1)*tau+((v2**2)/(2*a2)-(v1**2)/(2*a1))+l1*2+safe_d
    print(a,b,d)
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
    def __init__(self,num,V,sp):
        self.velocity=V.get_velocity()
        self.velocity.x=velocity
        self.num=num-1
        self.V=V
        self.sp=sp
        self.list=[]
        self.list.append(self.V)
        self.V.set_target_velocity(self.velocity)
        self.i=0
    def next(self):
        if self.num>0:
            vec = self.sp.rotation.get_forward_vector()
            rss_d=getrss(self.V,self.i,self.i+1)
            self.sp.location = self.sp.location + carla.Location(-rss_d * vec.x / np.sqrt((vec).dot(vec)), -rss_d * 
            #self.sp.location = self.sp.location + carla.Location(-rss_d , -rss_d *
vec.y / np.sqrt((vec).dot(vec)), 1)
            follower = world.spawn_actor(bp, self.sp)
            self.V=follower
            self.V.set_target_velocity(self.velocity)
            self.list.append(self.V)
            actor_list.append(follower)
            self.i=self.i+1
            self.num=self.num-1
            self.next()
    def get_list(self):
        return self.list






actor_list = []
try:
    client = carla.Client('localhost', 2000)
    client.set_timeout(2.0)
    world = client.get_world()
    world = client.load_world('Town05')

    blueprint_library = world.get_blueprint_library()

    bp = blueprint_library.filter('model3')[0]
    print(bp)

    spawn_point = world.get_map().get_spawn_points()[126]

    target = world.spawn_actor(bp, spawn_point)

    actor_list.append(target)
    obj=spawn(num,target,spawn_point)
    obj.next()
    list=obj.get_list()
    spectator = world.get_spectator()
    actor_list.append(spectator)
    while True:

        time.sleep(3)
        for i in range(num):
            if i!=1:
                list[i].apply_control(carla.VehicleControl(brake=1.0, steer=0))
            else:
                list[i].apply_control(carla.VehicleControl(brake=0.5, steer=0))
            transform = list[2].get_transform()
            spectator.set_transform(
            carla.Transform(transform.location + carla.Location(z=200), carla.Rotation(pitch=-90)))
            time.sleep(tau)


finally:
    print('destroying actors')
    for actor in actor_list:
        actor.destroy()
