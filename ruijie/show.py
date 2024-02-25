'''
Descripttion: 
version: 
Author: 胡睿杰
Date: 2024-01-27 11:22:45
LastEditors: Andy
LastEditTime: 2024-02-25 20:37:20
'''
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString
from pyproj import CRS, Transformer
from read import readtxt, dict_data  # Assuming readtxt and dict_data functions are defined in the 'read' module
from multiprocessing import Pool
from tqdm import tqdm
from functools import partial
from shapely.ops import transform
from functools import partial
import pyproj
import matplotlib.cm as cm
import matplotlib.patches as mpatches
from pyproj import CRS, Transformer, Proj

def plot_road(trajectory, width=22.5, style='-', color='black'):
    line = LineString(trajectory)
    # 创建一个转换器，将WGS84坐标转换为UTM坐标
    transformer = Transformer.from_crs('epsg:4326', 'epsg:32650', always_xy=True)
    line_transformed = transform(transformer.transform, line)
    # 创建道路的两侧线
    left_line = line_transformed.parallel_offset(width / 2, 'left')
    right_line = line_transformed.parallel_offset(width / 2, 'right')
    # 将UTM坐标转换回WGS84坐标
    transformer = Transformer.from_crs('epsg:32650', 'epsg:4326', always_xy=True)
    left_line = transform(transformer.transform, left_line)
    right_line = transform(transformer.transform, right_line)
    # 绘制道路的两侧线
    ax.plot(*left_line.xy, style, color=color)
    ax.plot(*right_line.xy, style, color=color)

def check_point_on_road(args):
    point_data, trajectories, i = args
    point = Point(point_data['lon'], point_data['lat'])
    for trajectory in trajectories:
        road = LineString(trajectory)
        if road.buffer(0.0002).contains(point):  # Adjust the buffer size as needed
            return (point_data['lon'], point_data['lat'], str(point_data['time']), i)
    return None

def plot_trajectories(trajectories, dict_data):
    colors = cm.rainbow(np.linspace(0, 1, len(dict_data)))
    args = []
    patches = [] #图例
    for i, (car_id, car_data) in enumerate(dict_data.items()):
        for point_data in car_data:
            args.append((point_data, trajectories, i))
        patches.append(mpatches.Patch(color=colors[i], label=car_id))

    with Pool() as p:
        for result in tqdm(p.imap(check_point_on_road, args), total=len(args)):
            if result is not None:
                lon, lat, time, i = result
                ax.scatter(lon, lat, color=colors[i])

    plt.legend(handles=patches)

if __name__ == "__main__":
    file = './路网数据/东二环.txt'
    with open(file, 'r') as f:
        data = eval(f.read())

    readtxt('log.txt')

    fig, ax = plt.subplots(figsize=(10, 8))

    # 绘制道路
    for trajectory in data:
        plot_road(trajectory)

    plot_trajectories(data, dict_data)

    plt.axis('equal')
    plt.show()