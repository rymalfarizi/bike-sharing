import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st


def create_daily_people_df(df):
    daily_people_df = df.resample(rule='D',on='dteday').agg({
        "hr" : "count",
        "cnt" : "sum"
    })
    daily_people_df = daily_people_df.reset_index()
    daily_people_df.columns = ['dteday', "hours_cnt",'people_count']
    return daily_people_df

def create_bymonth_df(df):
    monthly_df = df.resample(rule='M', on='dteday').cnt.sum()
    monthly_df.index = monthly_df.index.strftime('%Y-%m')
    monthly_df = monthly_df.reset_index()
    monthly_df.columns = ['dtemonth','cnt']
    return monthly_df

def create_byweather_df(df):
    weather_df = df.groupby(by='weathersit').agg({
    "hr" : "count",
    "cnt" : "sum"
    })
    weather_df.columns = ['cnthour', 'cntpeople']
    weather_df['Mean'] = weather_df['cntpeople'] / weather_df['cnthour']
    weather_df['weathersit'] = ['Clear', 'Cloudy','Light', 'Heavy']
    return weather_df

def create_byseason_changes_df(df):
    # Mencari season shift
    df['season_shift'] = df['season'].shift(1)

    # Temukan baris di mana season berubah (yaitu, ketika season tidak sama dengan season_shift)
    season_changes = df[df['season'] != df['season_shift']]

    # Hanya ambil kolom dteday dan season
    season_changes = season_changes[['dteday', 'season']]
    season_changes['dteday'] = season_changes['dteday'].dt.strftime('%Y-%m')
    season_changes.rename(columns={
        'dteday' : 'dtemonth'
    },inplace=True)

    season_mapping = {1: 'Spring', 2: 'Summer', 3: 'Autumn', 4: 'Winter'}
    season_changes['season'] = season_changes['season'].map(season_mapping)

    return season_changes

byhour_bike_df = pd.read_csv('dashboard/hour_bike_df.csv')
byhour_bike_df['dteday'] = pd.to_datetime(byhour_bike_df['dteday'])

# Membuat komponen filter
min_date = byhour_bike_df['dteday'].min()
max_date = byhour_bike_df['dteday'].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image('https://cdn0-production-images-kly.akamaized.net/O4WoUpvIW6ljnY-FBmd2n0ePtnc=/800x450/smart/filters:quality(75):strip_icc():format(webp)/kly-media-production/medias/3008248/original/043150000_1577671676-a.jpg')
    # Mengambil start_date & end_date dari data_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = byhour_bike_df[(byhour_bike_df['dteday'] >= str(start_date)) & 
                         (byhour_bike_df['dteday'] <= str(end_date))]

daily_people_df = create_daily_people_df(main_df)
bymonth_bike_df = create_bymonth_df(main_df)
byweather_bike_df = create_byweather_df(main_df)
byseason_changes_df = create_byseason_changes_df(main_df)

# Melengkapi dashboard dengan berbagai visualisasi data
# Header
st.header('Bike Sharing Report :sparkles:')
# informasi daily
st.subheader('Number of Cycles')

col1,col2 = st.columns(2)

with col1:
    people_count = daily_people_df.people_count.sum()
    st.metric('People Count', value=people_count)
with col2:
    hours_count = daily_people_df.hours_cnt.sum()
    st.metric("Average People/Hours", value=round(people_count/hours_count))


fig,ax = plt.subplots(figsize=(25,10))
ax.plot(
    bymonth_bike_df['dtemonth'],
    bymonth_bike_df['cnt'],
    marker='o',
    linewidth=2,
    color = "#90CAF9"
)

colors = ['green', 'orange', 'red', 'blue', 'green', 'orange', 'red', 'blue', 'green']
for color,season,season_change in zip(colors,byseason_changes_df['season'],byseason_changes_df['dtemonth']):
    ax.axvline(x=season_change, color=color, linestyle='--', label=season)
    ax.text(season_change, 100000, season, fontsize=20, color=color, ha='center')

ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

# Best and Worst Weather
st.subheader("Best & Worst Weather for Cycling")


fig, ax = plt.subplots(nrows=1,ncols=3,figsize=(30,6))
colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]

sns.barplot(y="cnthour", x="weathersit", data=byweather_bike_df, palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("By Hours", loc="center", fontsize=25)
ax[0].tick_params(axis ='x', labelsize=15)

sns.barplot(y="cntpeople", x="weathersit", data=byweather_bike_df, palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("By People", loc="center", fontsize=25)
ax[1].tick_params(axis ='x', labelsize=15)

sns.barplot(y="Mean", x="weathersit", data=byweather_bike_df, palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title("By Average", loc="center", fontsize=25)
ax[2].tick_params(axis ='x', labelsize=15)

st.pyplot(fig)

st.caption('Copyright (c) Rayhan Muhammad Alfarizi 2024')
