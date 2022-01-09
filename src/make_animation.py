# %%
import pandas as pd
import numpy as np

FPS = 10
FPD = 5

# Number of bars
bars = 30

df = pd.read_csv('data/coronavirus-cases-linear.csv', index_col='date', parse_dates=['date']).astype('float64').fillna(0)
df_ranked = df.replace(0,np.nan).rank(axis=1, method='first', ascending=False)

df_best = df_ranked.apply(np.nanmin)

def expand_table(df):
    df_indexed = df.reset_index()
    num_rows = FPD*len(df.index)
    df_indexed.index *= FPD
    df_indexed = df_indexed.reindex(range(0, num_rows))
    df_indexed['date'].interpolate(method='pad', inplace=True)
    for column in df_indexed.columns[1:]:
        df_indexed[column].interpolate(method='linear', inplace=True)
    return df_indexed.set_index('date')

df_expanded = expand_table(df)
ranked_expanded = expand_table(df_ranked)

from matplotlib import animation
from matplotlib.animation import FuncAnimation
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.transforms import Bbox
import matplotlib.ticker as ticker
from matplotlib.colors import hsv_to_rgb
import random

BAR_WIDTH = 0.8

def is_dark(c):
    return (c[0] * 0.299) + (c[1] * 0.587) + (c[2] * 0.114) < 0.5

def configure_chart():
    fig = plt.figure(figsize=(16,9), dpi=80)
    ax = plt.axes()
    ax.set_ylim(0, bars + 1)
    ax.invert_yaxis()
    ax.ticklabel_format(style='plain')
    ax.grid(visible=True, which='both', axis='x')
    ax.set_axisbelow(True)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.title(f'Total Coronavirus Cases By Country', fontsize=30)

def get_bbox(text):
    # get text bounding box in figure coordinates
    renderer = fig.canvas.get_renderer()
    bbox_text = text.get_window_extent(renderer=renderer)

    # transform bounding box to data coordinates
    return Bbox(ax.transData.inverted().transform(bbox_text))


configure_chart()
countries = df.columns
country_colors = {country:hsv_to_rgb((random.random(), 1, 1)) for country in countries}

used_artists = []
def animate(i):
    global used_artists
    # Push down rankings > bars some more during animation
    def alter(rank):
        if rank > bars:
            return rank * 2 - bars
        else:
            return rank
    for artist in used_artists:
        artist.remove()
    used_artists.clear()
    
    countries = [country for country, rank in ranked_expanded.iloc[i].items() if rank < bars + 1]
    ranks = [alter(rank) for country, rank in ranked_expanded.iloc[i].items() if country in countries]
    values = [value for country, value in df_expanded.iloc[i].items() if country in countries]
    colors = [country_colors[country] for country in countries]
    
    bars_object = ax.barh(ranks, values, color=colors, tick_label=countries)
    used_artists.append(bars_object)
    used_artists += ax.bar_label(bars_object, labels=[f' {int(value):,}' for value in values], label_type='edge', fontsize=8)
    for rank, value, country in zip(ranks, values, countries):
        color = 'white' if is_dark(country_colors[country]) else 'black'
        text = ax.text(value, rank, country + ' ', horizontalalignment='right', verticalalignment='center', color=color)
        bbox = get_bbox(text)
        # Check if text fits
        if bbox.width > value:
            text.remove()
        else:
            used_artists.append(text)
        
    date_str = df_expanded.index[i].strftime('%Y-%m-%d')
    used_artists.append(ax.text(0.8, 0.2, date_str, transform=ax.transAxes, fontsize=60, horizontalalignment='center', verticalalignment='center'))
    
    # Rewrite the x countries
    x_countries = ax.get_xticks()
    ax.xaxis.set_major_formatter(ticker.EngFormatter())
    
    ax.set_xlim(right=max(values)/0.9)
    

anim = FuncAnimation(fig=fig, func=animate, frames=len(df_expanded.index), interval=1000/FPS, repeat=False)
plt.show()
