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

def plot_trajectory(dfs, pic_name='evtTimePoint',grid=False, evt=0):
    """Plots the trajectory of points from a DataFrame.

    Args:
        df: Pandas DataFrame with 'positionTime' (datetime) and 'position' (dict).
    """
    x_min=302491 - 302491
    x_max=302516 - 302491
    y_min=2770397 - 2770397
    y_max=2770422 - 2770397
    scale = 45
    grid_size = 45
    
    fig, ax = plt.subplots(figsize=(10, 10))  # adjust figsize for better view
    # Load the image
    img = Image.open('../databank/ED_Area.png')
    img_array = np.array(img)
    img_array = np.flipud(img_array)     
    ax.imshow(img_array)
    
    colors = {'N002':'blue',
              'N015':'violet',
              'N016':'limegreen',
              'N031':'darkorange',
              'N006':'tomato',
              'N007':'royalblue',
              'N008':'peru',
              'N017':'salmon',
              'N029':'peru',
              'N030':'blue'}

    if evt == 0:
        # i want to plot the ground turth route on the map
        # y=6 start from x=5 to x=20.5 then 
        # x=20.5  from y=6 to y=23.5 then
        # y=23.5 from x=20.5 to x= 12.5 then
        # x=12.5 from y=23.5 to y=8 then
        # y=8 from x=12.5 to x=5, start plot the route
        x = [5,20.5,20.5,12.5,12.5,5]
        y = [6,6,23.5,23.5,8,8]
        x = scale*np.array(x)
        y = scale*np.array(y)
        ax.plot(x, y, color='red', alpha = 0.5, linestyle = '-',linewidth=10)
    elif evt==1:
        # i want to plot the ground turth route on the map
        # x=4  from y=9 to y=14.5 then
        # y=14.5 from x=4 to x= 9 
        # start plot the route
        x = [4,4,10]
        y = [9,14.5,14.5]
        x = scale*np.array(x)
        y = scale*np.array(y)
        ax.plot(x, y, color='red', alpha = 0.5, linestyle = '-',linewidth=10)

    total_points = 0
    for k,d in dfs.items():
        df = d.copy()
        total_points += len(df)
        # Extract x and y coordinates; handle potential errors.
        x = scale*(df['x']-x_min)
        y = scale*(df['y']-y_min)
        
        df['time_diff'] = df['positionTime'].diff().dt.total_seconds()
        
        times = df['positionTime'].values
        
        # Calculate alpha values for transparency (optional)
        alpha_values = np.linspace(0.0, 0.75, len(x)) # Adjust transparency as needed
        r, g, b = to_rgb(colors[k])
        clr = [(r, g, b, alpha) for alpha in np.floor(alpha_values*10)/10]
        
        # Plot points with transparency
        ax.scatter(x, y, c = clr, alpha=0.5, s = 15)

        # Add a line connecting the points
        consecutive_indices = np.where(df['time_diff'].values > 10)
        if consecutive_indices[0].size > 1:
            cons_i = 0
            for i, idx in enumerate(consecutive_indices[0]):
                if i == consecutive_indices[0].size-1:
                    x_consecutive = x[cons_i:]
                    y_consecutive = y[cons_i:]
                else:
                    x_consecutive = x[cons_i:idx]
                    y_consecutive = y[cons_i:idx]
                    cons_i=idx                
                ax.plot(x_consecutive, y_consecutive, color=colors[k], alpha = 0.1, linestyle = '-')
        else:
            ax.plot(x, y, color=colors[k], alpha = 0.1, linestyle = '-') 

    # Set plot limits
    major_ticks = np.arange(0, 25, 1)
    ax.grid(which='major', alpha=0.5, linestyle='--')
    ax.set_xticks(major_ticks * grid_size)
    ax.set_yticks(major_ticks * grid_size)
    ax.set_xticklabels(major_ticks)
    ax.set_yticklabels(major_ticks)
    if(not grid):
        plt.xticks([])
        plt.yticks([])
    
    ax.set_xlim(0,scale*(x_max-x_min))
    ax.set_ylim(0,scale*(y_max-y_min))
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title(f'Position Trajectory_{pic_name}_{total_points}points')

    # plt.axis('off')
    plt.grid(True)
    filename = f'../output/val/{pic_name}.png'
    os.makedirs(os.path.dirname(filename),exist_ok=True)

    plt.savefig(fname=filename)
    print(f' === complete {pic_name} image === ')

# Draw Trajectory 
def Trajectory_plot(events, drawPds,mins=1,flag='origin',grid=False):
    for i, evt in events.iterrows():
        print(f' == work on {i} event == ')
        endtime = evt['endTime']
        startTime = evt['startTime']
        
        # if i != 30:
        #     continue
        dfs = {}
        for beacon in select_beacons:
            df = drawPds[beacon].loc[(drawPds[beacon]['positionTime'] >= startTime) & (drawPds[beacon]['positionTime'] <= endtime)]    
            if len(df) > 0:
                dfs[beacon]=df
        
        plot_trajectory(dfs, pic_name=f'{i+1}_{endtime.hour}{endtime.minute}', grid=grid, evt=i)
 
# Load the event timePoint
events = pd.read_excel("../databank/events_val_route.xlsx",dtype={'日期':str,'開始時間':str,'結束時間':str})
# events['positionTime'] = pd.to_datetime(events['日期'] + ' ' + events['時間'], format='%Y%m%d %H%M', errors='coerce').dt.tz_localize(local_timezone)
events['startTime'] = pd.to_datetime(events['日期'] + ' ' + events['開始時間'], format='%Y%m%d %H%M%S', errors='coerce').dt.tz_localize(local_timezone)
events['endTime'] = pd.to_datetime(events['日期'] + ' ' + events['結束時間'], format='%Y%m%d %H%M%S', errors='coerce').dt.tz_localize(local_timezone)

Trajectory_plot(events, txyzPds,1,'filter_0',grid=True)       
