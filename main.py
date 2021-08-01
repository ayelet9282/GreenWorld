import matplotlib.pyplot as plt
from matplotlib import colors

from geodata_functions import *
import glob
import re
import geopandas
from flask import Flask



files = [f for f in glob.glob("C:/Users/אילת/Desktop/שיעורים/python/Project/data/csse_*.csv")]

dfs = []
columns = ['Province/State', 'Country/Region', 'Last Update', 'Confirmed']
for f in files:
    df = pd.read_csv(f, parse_dates=['Last Update'], usecols=columns)
    dfs.append(df)

df = pd.concat(dfs)
print(df)
df['Country/Region']=df['Country/Region'].str.replace('UK','United Kingdom')
print(df)
def to_state(row):
    ps=row['Province/State']
    if  pd.isna(ps):
        return ps
    match1=re.match(r'\w+[ \-]?\w+, ([A-Z]{2})$',ps)
    print(match1)
    if match1 is None:
        print('-----------------------')
        return row['Province/State']
    print('##########')
    reg=match1.groups()

    print('-------------------------------------------------')

    return states_abbr_to_full[reg[0]]
df['Province/State']=df.apply(to_state,axis=1)
pd.set_option('display.max_rows',df.shape[0]+1)
print(df)
df['Location'] = df.apply(create_location, axis=1)
print(df['Location'])
print(len(df['Location'].value_counts()))
######################level2
lastUpdate=df['Last Update'].unique().tolist()
dates=sorted(lastUpdate)
print(dates)
date_rng=pd.date_range(start=dates[0],end=dates[len(dates)-1],freq='D')
print(date_rng)
location_timesreies={}
location_details={}
locations=df['Location'].unique().tolist()
for item in locations:
    values=df.loc[df['Location']==item]
    ldf=values.set_index('Last Update').resample('D').mean()
    print(ldf)
    ldf=ldf.reindex(index=date_rng)
    location_timesreies[item]=ldf.fillna(method='ffill')
    location_details[item] = {'Province/State': values.iloc[0]["Province/State"],
                           'Country/Region': values.iloc[0]['Country/Region']}
#print(location_timesreies)

print(location_details['Sweden'])
daily_confirmed=pd.DataFrame(index=date_rng,columns=locations)
for location in locations:
    daily_confirmed[location]=location_timesreies[location]
print(daily_confirmed)
#######3
def build_df_for_datetime(d):
    day_df=pd.DataFrame(daily_confirmed.loc[d])
    day_df.columns=['Confirmed']
    day_df[['Province/State','Country/Region']]= day_df.apply(lambda  x: pd.Series(location_details[x.name]),axis=1)
    day_df.dropna(subset=['Confirmed'],inplace=True)
    return  day_df
print(build_df_for_datetime(date_rng[0]))
day=build_df_for_datetime(date_rng[0])
ncov=build_ncov_geodf(day)
ncov=ncov.sort_values('Confirmed')
print('------------')
print(ncov[['name','Confirmed','geometry']])
COLOR = 'black'
plt.rcParams['text.color'] = COLOR
plt.rcParams['axes.labelcolor'] = COLOR
plt.rcParams['xtick.color'] = COLOR
plt.rcParams['ytick.color'] = COLOR

world_lines = geopandas.read_file('zip://./files/ne_50m_admin_0_countries.zip')
world = world_lines[(world_lines['POP_EST'] > 0) & (world_lines['ADMIN'] != 'Antarctica')]
fig,ax=plt.subplots(figsize=(18, 6))
world.plot(
    ax=ax,
    color = "lightslategray",
    edgecolor = "slategray",
    linewidth = 0.5);
ax.axis('off')

ax.set_title(date_rng[0].strftime("%b %d %Y"))
ncov = build_ncov_geodf(day)

ncov.plot(
    ax=ax,
    column='Confirmed',
    norm=colors.LogNorm(vmin=1, vmax=1000),
    legend=True,
    legend_kwds={'label': "Confirmed 2019-nCoV Cases"},
    cmap='OrRd')
#plt.show()
app = Flask('__name__')
def output_images():
    i=0

    for x in date_rng:
        fig, ax = plt.subplots(figsize=(18, 6))
        world.plot(
            ax=ax,
            color="lightslategray",
            edgecolor="slategray",
            linewidth=0.5);
        ax.axis('off')
        ax.set_title(x.strftime("%b %d %Y"))
        day=build_df_for_datetime(x)

        ncov = build_ncov_geodf(day)
        ncov.plot(
            ax=ax,
            column='Confirmed',
            norm=colors.LogNorm(vmin=1, vmax=1000),
            legend=True,
            legend_kwds={'label': "Confirmed 2019-nCoV Cases"},
            cmap='OrRd')
        fig.savefig('./static/image/map' + str(i) + '.png', facecolor='slategrey', dpi=150, bbox_inches='tight')
        i=i+1
output_images()