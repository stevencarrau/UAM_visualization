import json
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math
from ast import literal_eval
from matplotlib.animation import FuncAnimation
import numpy as np
from aircraft import Aircraft
from vertiports import Vertiports
import random
random.seed(4)


# ---------- PART 1: Globals for visualization
# plt.rcParams['savefig.bbox'] = 'tight'
n_agents = 20
my_dpi = 96
Writer = matplotlib.animation.writers['ffmpeg']
writer = Writer(fps=33, metadata=dict(artist='Me'), bitrate=1800)
fig = plt.figure(figsize=(2000/my_dpi, 1600/my_dpi), dpi=my_dpi,frameon=False)
fig.set_tight_layout('True')
img = plt.imread("mapimage.jpeg")
my_palette = plt.cm.get_cmap("tab10",n_agents)
frames = 100
ax = plt.subplot()
ax.imshow(img,extent=[-15,15,-10,10])
ax.set_xlim(-15,15)
ax.set_ylim(-10,10)
# ax.axis('tight')
ax.axis('off')
plt.hsv()
SF_GPS = (37.773972,-122.431297)
prev_time= 0
j = 0


# ----------- PART 2: Time loop for visualization - called in FuncAnimate()

def update(i):
    global prev_time, j, vehicle_queue, verts
    dt = 0.2
    print(i)
    land_s = False
    if time_policy:
        t_i = i*dt
        # If aircraft takes off at this timestamp
        if time_policy.get(t_i):
            # Usable cache of 8 aircraft in towers requests
            for v_i in time_policy[t_i]:
                if len(verts.findTower_ind(time_policy[t_i][v_i][-1]).vehicle_array) < 8:
                    track = verts.convertTrack(time_policy[t_i][v_i])
                    vehicle_array.append(Aircraft(loc=tuple(verts.array[time_policy[t_i][v_i][0]].loc_gps)+(100,),POV_center=SF_GPS,col=(0,1,0),ax=ax,track=track,track_col=my_palette(j),land_tower=verts.findTower(time_policy[t_i][v_i][-1]),land_wp=time_policy[t_i][v_i][-1]))
                    verts.findTower_ind(time_policy[t_i][v_i][-1]).add_vehicle(vehicle_array[-1])
                    j += 1
                # If full then keep a queue to add to next tower
                else:
                    track = verts.convertTrack(time_policy[t_i][v_i])
                    vehicle_queue.append((v_i,tuple(verts.array[time_policy[t_i][v_i][0]].loc_gps)+(100,),track,verts.findTower(time_policy[t_i][v_i][-1]),time_policy[t_i][v_i][-1],time_policy[t_i][v_i][-1]))
        # No aircraft in take-off but can be assigned to request cache in this time-step
        else:
            for v_i,v_q in enumerate(vehicle_queue):
                if len(verts.findTower_ind(v_q[5]).vehicle_array) < 8:
                    v_q = vehicle_queue.pop(v_i)
                    vehicle_array.append(Aircraft(loc=v_q[1],POV_center=SF_GPS,col=(0,1,0),ax=ax,track=v_q[2],track_col=my_palette(j),land_tower=v_q[3],land_wp=v_q[4]))
                    verts.findTower_ind(v_q[5]).add_vehicle(vehicle_array[-1])
                    j += 1

    # Artist array for plotting
    artist_array = []
    landed_drones = []
    # Cycle through the schedulers for requests
    for t_i in verts.towers:
        if t_i.allocating_flag:
            t_i.queue_full = True
            t_i.activeRequest()

    clear_requests = []
    # Cycle through schedulers for allocations
    for t_i in verts.towers:
        for ind,v_ind in enumerate(t_i.vehicle_array):
            if t_i.active_request:
                if v_ind+1 in t_i.active_request['Allocate']:
                    land_s = verts.array[t_i.landWaypoint(ind)].loc_xy
                    print(land_s)
                    clear_requests.append(t_i)
            artist_array += t_i.vehicle_array[v_ind].simulate(dt, land_signal=land_s, operating_number=list(t_i.vehicle_array.values()).index(t_i.vehicle_array[v_ind]))
            land_s = False
            if t_i.vehicle_array[v_ind].kill:
                landed_drones.append(t_i.vehicle_array[v_ind])

    # Remove landed drones from scheduler
    for v_i in landed_drones:
        verts.findTower_ind(v_i.land_wp).remove_vehicle(v_i)
        verts.findTower_ind(v_i.land_wp).requestLanded()
        vehicle_array.remove(v_i)

    # Update visuals on towers
    for t_i in verts.towers:
        out_art = t_i.towerUpdate()
        if out_art: artist_array.append(out_art)
    prev_time = i

    return artist_array

def schedules(filename):
    policy = dict()
    vehicles = set()
    veh_no = 0
    start_time = 21633
    with open(filename) as fp:
        for line in fp:
            line = line.split(',')
            if line[2] not in allowed_ports+second_tower+third_tower:
                line[2] = random.choice(allowed_ports+second_tower+third_tower)
            policy[int(float(line[0]))-start_time] = dict({veh_no:line[1:3]})
            vehicles.add(veh_no)
            veh_no += 1
    return vehicles, policy


def policies(filename):
    policy = dict()
    vehicles = set()
    with open(filename) as fp:
        for line in fp:
            line = line.split()
            if 'Time:' in line:
                time = int(line[1])
            else:
                if policy.get(line[0]):
                    policy[line[0]][time] = line[1:]
                else:
                    policy[line[0]] = dict()
                    policy[line[0]][time] = line[1:]
                vehicles.add(line[0])
    return vehicles, policy


no_towers = 2
verts = Vertiports(POV_center=SF_GPS)
verts.addPorts('Scenarios/areacre.txt')
verts.towerClusters(10) # 10 tower clusters
verts.plotTowers(ax)
time_policy = []
# Check these ports corresspond to the towers
allowed_ports = ['WP52','WP555','WP322']
second_tower = ['WP802','WP989','WP778']
third_tower = ['WP94','WP661','WP9']
verts.findTower_ind(allowed_ports[2]).towerSchedules('Scenarios/test_medium19.csv',allowed_ports)
verts.findTower_ind(second_tower[2]).towerSchedules('Scenarios/test_medium40_csv.csv',second_tower)
verts.findTower_ind(third_tower[2]).towerSchedules('Scenarios/test_medium40_csv.csv',third_tower)

vehicles, time_policy = schedules('Scenarios/scn_UAM_testNewVT.trp')
vehicle_array = []
vehicle_queue = []
i = 0
if time_policy:
    pass
else:
    for v_i in vehicles:
        track = verts.convertTrack(policy[v_i])
        vehicle_array[v_i] = Aircraft(loc=tuple(verts.array[policy[v_i][0][0]].loc_gps)+(100,), POV_center=SF_GPS,col=(0,1,0),ax=ax,track=track,track_col=my_palette(i))
        i+=1

# For showing video
ani = FuncAnimation(fig, update, frames=500, interval=0.04, blit=True,repeat=False)
plt.show(block=True)

# For saving video
# ani = FuncAnimation(fig, update, frames=1000,repeat=False)
# ani.save('Two_tower_allocation_decen.mp4',writer = writer)
