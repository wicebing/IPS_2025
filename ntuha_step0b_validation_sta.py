import pandas as pd
import numpy as np
from PIL import Image
import datetime,os,math, pytz, json, pickle
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.colors as mcolors
from matplotlib.colors import to_rgb, to_rgba

import utils

databank_filepath = "../databank/positions_VAL"
os.makedirs(databank_filepath,exist_ok=True)

local_timezone = pytz.timezone('Asia/Taipei') 
 
select_beacons =['N002', 'N015', 'N016', 'N031']
beacon_ids = select_beacons #utils.get_beacons()
print('=== load beacons ids ===')

x_min=302491
x_max=302516
y_min=2770397
y_max=2770422
scale = 45
grid_size = 45
txyzPds = {}

for beacon in beacon_ids:
    recordName= f'{beacon}.pkl'
    pickle_filepath = os.path.join(databank_filepath,recordName)
    
    if os.path.isfile(pickle_filepath):
        print(f'=== {beacon}.pkl exist, loading ===')

        txyzPd_origin = pd.read_pickle(pickle_filepath)
        pd_pz = pd.json_normalize(txyzPd_origin['position'])
        pd_time = pd.to_datetime(txyzPd_origin['positionTime'],format='mixed').dt.tz_convert(local_timezone)
        df = pd.concat([pd_time,pd_pz],axis=1)
        
        df['x'] = df['x']-x_min
        df['y'] = df['y']-y_min
        
        txyzPds[beacon]=df

def calculate_distance_to_route(x, y, route):
    """Calculate the minimum distance from a point to a route line segment."""
    def point_to_segment_distance(px, py, ax, ay, bx, by):
        """Calculate the distance from point (px, py) to line segment (ax, ay) - (bx, by)."""
        if (ax, ay) == (bx, by):
            return np.sqrt((px - ax)**2 + (py - ay)**2)
        else:
            t = max(0, min(1, ((px - ax) * (bx - ax) + (py - ay) * (by - ay)) / ((bx - ax)**2 + (by - ay)**2)))
            proj_x = ax + t * (bx - ax)
            proj_y = ay + t * (by - ay)
            return np.sqrt((px - proj_x)**2 + (py - proj_y)**2)

    distances = [point_to_segment_distance(x, y, route[i][0], route[i][1], route[i+1][0], route[i+1][1]) for i in range(len(route) - 1)]
    return min(distances)

def get_ground_truth_route(evt):
    """Get the ground truth route based on the event index."""
    if evt == 0:
        return [(5, 6), (20.5, 6), (20.5, 23.5), (12.5, 23.5), (12.5, 8), (5, 8)]
    elif evt == 1:
        return [(4, 9), (4, 14.5), (10, 14.5)]
    return []

def analyze_position_error(events, drawPds):
    results = []
    for i, evt in events.iterrows():
        print(f' == analyzing {i} event == ')
        endtime = evt['endTime']
        startTime = evt['startTime']
        ground_truth_route = get_ground_truth_route(i)
        ground_truth_route = [((x - x_min), (y - y_min)) for x, y in ground_truth_route]

        for beacon in select_beacons:
            df = drawPds[beacon].loc[(drawPds[beacon]['positionTime'] >= startTime) & (drawPds[beacon]['positionTime'] <= endtime)]
            if len(df) > 0:
                df['x_scaled'] = (df['x'] - x_min)
                df['y_scaled'] = (df['y'] - y_min)
                df['distance_to_route'] = df.apply(lambda row: calculate_distance_to_route(row['x_scaled'], row['y_scaled'], ground_truth_route), axis=1)
                df['event'] = i
                df['beacon'] = beacon
                results.append(df[['positionTime', 'x', 'y', 'distance_to_route', 'event', 'beacon']])

    result_df = pd.concat(results, axis=0, ignore_index=True)
    return result_df
 
# Load the event timePoint
events = pd.read_excel("../databank/events_val_route.xlsx",dtype={'日期':str,'開始時間':str,'結束時間':str})
# events['positionTime'] = pd.to_datetime(events['日期'] + ' ' + events['時間'], format='%Y%m%d %H%M', errors='coerce').dt.tz_localize(local_timezone)
events['startTime'] = pd.to_datetime(events['日期'] + ' ' + events['開始時間'], format='%Y%m%d %H%M%S', errors='coerce').dt.tz_localize(local_timezone)
events['endTime'] = pd.to_datetime(events['日期'] + ' ' + events['結束時間'], format='%Y%m%d %H%M%S', errors='coerce').dt.tz_localize(local_timezone)

# Analyze position error
position_error_df = analyze_position_error(events, txyzPds)
position_error_df.to_csv('../output/analysis/position_error_analysis.csv', index=False)

