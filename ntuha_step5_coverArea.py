import pandas as pd
import numpy as np
from PIL import Image
import datetime,os,math, pytz, json, pickle
from functools import reduce
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
from matplotlib.colors import to_rgb, to_rgba

import utils

databank_filepath = "../databank/positions"
os.makedirs(databank_filepath,exist_ok=True)

local_timezone = pytz.timezone('Asia/Taipei') 
 
select_beacons =['N002', 'N003', 'N004', 'N005', 'N006', 'N007', 'N008', 'N017']
beacon_ids = select_beacons #utils.get_beacons()
print('=== load beacons ids ===')

x_min=302491
x_max=302516
y_min=2770397
y_max=2770422
scale = 45
grid_size = 45

# Define coordinates to remove
all_area_coords = set()
for i in range(25):   # grid_x <= 7 (0-7)
    for j in range(25):  # grid_y >= 16
        all_area_coords.add((i, j))
remove_coords = set()
for i in range(25):  # Or range(25) if your grid is actually 0-24
    remove_coords.add((0, i))     # grid_x = 0
    remove_coords.add((24, i))    # grid_x = 24
for j in range(25):  # Or range(25) if your grid is actually 0-24
    remove_coords.add((j, 0))     # grid_y = 0
    remove_coords.add((j, 24))    # grid_y = 24
for i in range(8):   # grid_x <= 7 (0-7)
    for j in range(16, 25):  # grid_y >= 16
        remove_coords.add((i, j))
for i in range(3):   # grid_x <= 7 (0-7)
    for j in range(13, 16):  # grid_y >= 16
        remove_coords.add((i, j))
for i in range(3):   # grid_x <= 7 (0-7)
    for j in range(13, 16):  # grid_y >= 16
        remove_coords.add((i, j))
for i in range(4,18):   # grid_x <= 7 (0-7)
    for j in range(5):  # grid_y >= 16
        remove_coords.add((i, j))
all_area_coords = all_area_coords-remove_coords

def preprocess_1(df, time_col='positionTime'):
    df = df.sort_values(by=time_col).copy()

    df['weekday'] = df[time_col].dt.weekday
    df['hour'] = df[time_col].dt.hour
    df['id_mins'] = df[time_col].dt.round('min')
    df['grid_x'] = np.floor(df['x']).astype(int)
    df['grid_y'] = np.floor(df['y']).astype(int)
    df['axis'] = tuple(zip(df['grid_y'], df['grid_x']))

    return df

# Load the beacon positionTime
with open("../databank/pkl/filter02_dt.pkl", 'rb') as f:
    txyzPds = pickle.load(f)

aao = []

for k,v in txyzPds.items():
    print(f' == load {k} == ')
    aao.append(preprocess_1(v))
combined_beacons = pd.concat(aao,axis=0, ignore_index=True)

# Group by id_mins and aggregate axis (coordinates) into a list
byMin_coverArea = combined_beacons.groupby('id_mins').agg({'axis': lambda x: list(x)})
byMin_coverArea = byMin_coverArea.reset_index()
byMin_coverArea.loc[:,['axis']] = byMin_coverArea['axis'].apply(set).apply(list)

# for each id_mins, in the list of axis, expand each coordinate to +2 -2
# expand like the following code
# def get_axis_values(row, heatmap_rows, heatmap_cols):
#         i, j = row['grid_x'], row['grid_y']
#         axis_values = []
#         x_min_index = max(0, i-3)
#         x_max_index = min(heatmap_cols - 1, i + 3)
#         y_min_index = max(0, j-3)
#         y_max_index = min(heatmap_rows - 1, j + 3)

#         for x_index in range(x_min_index, x_max_index + 1):
#             for y_index in range(y_min_index, y_max_index + 1):
#                 if (x_index == i-3 and y_index == j-3) or \
#                    (x_index == i+3 and y_index == j-3) or \
#                    (x_index == i-3 and y_index == j+3) or \
#                    (x_index == i+3 and y_index == j+3):
#                        continue  # Skip the corner cells.
#                 axis_values.append((x_index, y_index)) # Store as tuples
#         return axis_values
aa2 = byMin_coverArea.copy()
aa2.loc[:, ['axis_agg']] = aa2['axis'].apply(lambda k: reduce(lambda a, b: a.union(b), [
    set([(max(0, min(24, i)), max(0, min(24, j)))  # Clamp i and j
         for i in range(x - 2, x + 3)
         for j in range(y - 2, y + 3)])
    for x, y in k]))

def plot_coords(aa2, grid=False):
    for i, row in aa2.iterrows():
        id_mins = row['id_mins']
        axis_agg = row['axis_agg']
        axis = row['axis']

        x_min=302491 - 302491
        x_max=302516 - 302491
        y_min=2770397 - 2770397
        y_max=2770422 - 2770397
        scale = 45
        grid_size = 45

        # Load the image
        img = Image.open('../databank/ED_Area.png')
        img_array = np.array(img)
        img_array = np.flipud(img_array)

        heatmap_rows = img_array.shape[0] // grid_size
        heatmap_cols = img_array.shape[1] // grid_size

        fig, ax = plt.subplots(figsize=(10, 10))  # adjust figsize for better view
        ax.imshow(img_array)

        # Draw coordinates in axis_agg
        for coord in axis_agg:
            x, y = coord
            rect = mpatches.Rectangle((y * grid_size, x * grid_size), grid_size, grid_size,
                                      alpha=0.5, facecolor='yellow', edgecolor='yellow')
            ax.add_patch(rect)

        # Highlight coordinates in axis
        for coord in axis:
            x, y = coord
            rect = mpatches.Rectangle((y * grid_size, x * grid_size), grid_size, grid_size,
                                      alpha=0.5, facecolor='red', edgecolor='red')
            ax.add_patch(rect)

        # Set plot limits
        major_ticks = np.arange(0, 1125, grid_size)
        ax.grid(which='major', alpha=0.5, linestyle='--')
        ax.set_xticks(major_ticks)
        ax.set_yticks(major_ticks)
        if not grid:
            plt.xticks([])
            plt.yticks([])

        ax.set_xlim(0, scale * (x_max - x_min))
        ax.set_ylim(0, scale * (y_max - y_min))

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_title(f'Position heatmap_{id_mins.strftime("%Y%m%d_%H%M")}')

        pic_filepath = f'../output/coords/{id_mins.strftime("%Y%m%d_%H%M")}.png'
        os.makedirs(os.path.dirname(pic_filepath), exist_ok=True)

        plt.savefig(fname=pic_filepath)
        print(f' === complete {id_mins} image === ')

plot_coords(aa2)




