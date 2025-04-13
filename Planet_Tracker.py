import numpy as np
import matplotlib.pyplot as plt
from astropy.coordinates import EarthLocation, AltAz, get_body, get_sun
from astropy.time import Time
from astropy import units as u
import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title="Planet Tracker", layout="centered")

st.title("🪐 Planet & Sun Tracker")

# --- Location Input ---
st.subheader("📍 Enter Your Location")
latitude = st.number_input("Latitude (°)", value=13.00844, format="%.5f")
longitude = st.number_input("Longitude (°)", value=74.79777, format="%.5f")
location = EarthLocation(lat=latitude*u.deg, lon=longitude*u.deg)

# --- Time Input (IST) ---
st.subheader("🕒 Select Time (IST)")

# Initialize session state
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = datetime.now().date()
if 'selected_time' not in st.session_state:
    st.session_state.selected_time = (datetime.now() + timedelta(minutes=30)).time()

# Time input
col1, col2 = st.columns([2, 1])
with col1:
    selected_date = st.date_input("Choose a date", value=st.session_state.selected_date, key='selected_date')
    selected_time = st.time_input("Choose time (IST)", value=st.session_state.selected_time, key='selected_time')
with col2:
    if st.button("Use Current Time"):
        now = datetime.now()
        st.session_state.selected_date = now.date()
        st.session_state.selected_time = now.time()

# Combine inputs into datetime
slider_time_ist = datetime.combine(st.session_state.selected_date, st.session_state.selected_time)
slider_time_utc = slider_time_ist - timedelta(hours=5, minutes=30)

# AltAz frame
altaz = AltAz(location=location, obstime=Time(slider_time_utc))

# --- Track Planets and Sun ---
planets = {
    "mercury": "blue",
    "venus": "orange",
    "mars": "red",
    "jupiter": "green",
    "saturn": "purple",
    "uranus": "cyan",
    "neptune": "darkblue",
    "sun": "yellow"
}

altitudes = []
azimuths = []
labels = []
colors = []

sun = get_sun(Time(slider_time_utc)).transform_to(altaz)
is_night = sun.alt.degree < -6
is_day = sun.alt.degree > 0

for planet, color in planets.items():
    if planet == "sun":
        obj = sun
    else:
        obj = get_body(planet, Time(slider_time_utc), location).transform_to(altaz)
    if obj.alt.degree > 0:
        altitudes.append(obj.alt.degree)
        azimuths.append(obj.az.degree)
        labels.append(planet.capitalize())
        colors.append(color)

# --- Plotting ---
if not labels:
    st.info(f"No planets or Sun visible above the horizon at {slider_time_ist.strftime('%Y-%m-%d %H:%M IST')}.")
else:
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(8, 8))

    # Background color based on time
    if is_night:
        ax.set_facecolor('#0a0a23')
        alpha = 1.0
    elif is_day:
        ax.set_facecolor('#e5e6ae')
        alpha = 0.3
    else:
        ax.set_facecolor('#2c7491')
        alpha = 0.6

    azimuths_rad = np.radians(azimuths)
    altitudes_polar = 90 - np.array(altitudes)
    sizes = [200 if label == "Sun" else 100 for label in labels]

    ax.scatter(azimuths_rad, altitudes_polar, c=colors, s=sizes, alpha=alpha)

    for i, txt in enumerate(labels):
        ax.text(azimuths_rad[i], altitudes_polar[i], txt, fontsize=12, ha='right', color=colors[i], alpha=alpha)

    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_rmax(90)
    ax.set_rticks([30, 60, 90])
    ax.set_xticks(np.radians([0, 90, 180, 270]))
    ax.set_xticklabels(["0° (N)", "90° (E)", "180° (S)", "270° (W)"])

    from matplotlib.lines import Line2D
    legend_elements = [Line2D([0], [0], marker='o', color='w', label=labels[i], 
                              markerfacecolor=colors[i], markersize=14 if labels[i] == "Sun" else 10) 
                       for i in range(len(labels))]
    ax.legend(handles=legend_elements, loc="upper left", bbox_to_anchor=(-0.2, 1.0), fontsize=10)

    ax.grid(True, linestyle="--", alpha=0.6)
    title_color = 'white' if is_night else 'green'
    ax.set_title(f"🌍 Planets & Sun at {slider_time_ist.strftime('%Y-%m-%d %H:%M IST')}", 
                 fontsize=14, color=title_color, pad=30)

    st.pyplot(fig)
