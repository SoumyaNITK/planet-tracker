import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from astropy.coordinates import EarthLocation, AltAz, get_body, get_sun
from astropy.time import Time
from astropy import units as u
from datetime import datetime, timedelta

# --- Page Config ---
st.set_page_config(page_title="Planet Tracker 🪐", layout="wide")

st.title("🌍 Planet & Sun Tracker")
st.markdown("Visualize the positions of planets and the Sun based on your location and time.")

# --- Location Input ---
st.subheader("📍 Enter Your Location")
col1, col2 = st.columns(2)
lat = col1.number_input("Latitude (°)", value=13.00844, format="%.5f")
lon = col2.number_input("Longitude (°)", value=74.79777, format="%.5f")

location = EarthLocation(lat=lat * u.deg, lon=lon * u.deg)

# --- Time Input (IST) ---
st.subheader("🕒 Select Time (IST)")
selected_date = st.date_input("Choose a date", value=datetime.now().date())
selected_time = st.time_input("Choose time (IST)", value=(datetime.now() + timedelta(minutes=30)).time())

slider_time_ist = datetime.combine(selected_date, selected_time)
slider_time_utc = slider_time_ist - timedelta(hours=5, minutes=30)
time_utc = Time(slider_time_utc)
altaz = AltAz(location=location, obstime=time_utc)

# --- Planet Data ---
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

altitudes, azimuths, labels, colors = [], [], [], []

sun = get_sun(time_utc).transform_to(altaz)
is_night = sun.alt.degree < -6
is_day = sun.alt.degree > 0

for planet, color in planets.items():
    obj = sun if planet == "sun" else get_body(planet, time_utc, location).transform_to(altaz)
    if obj.alt.degree > 0:
        altitudes.append(obj.alt.degree)
        azimuths.append(obj.az.degree)
        labels.append(planet.capitalize())
        colors.append(color)

# --- Display Sky Plot ---
if not labels:
    st.warning(f"No planets or the Sun are visible at {slider_time_ist.strftime('%Y-%m-%d %H:%M IST')}.")
else:
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(8, 8))

    # Set sky color
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
    altitudes_plot = 90 - np.array(altitudes)
    sizes = [200 if label == "Sun" else 100 for label in labels]

    scatter = ax.scatter(azimuths_rad, altitudes_plot, c=colors, s=sizes, alpha=alpha)

    for i, txt in enumerate(labels):
        ax.text(azimuths_rad[i], altitudes_plot[i], txt, fontsize=12, ha='right', color=colors[i], alpha=alpha)

    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_rmax(90)
    ax.set_rticks([30, 60, 90])
    ax.set_xticks(np.radians([0, 90, 180, 270]))
    ax.set_xticklabels(["0° (N)", "90° (E)", "180° (S)", "270° (W)"])
    ax.grid(True, linestyle="--", alpha=0.6)

    from matplotlib.lines import Line2D
    legend_elements = [Line2D([0], [0], marker='o', color='w', label=labels[i],
                              markerfacecolor=colors[i], markersize=14 if labels[i] == "Sun" else 10)
                       for i in range(len(labels))]
    ax.legend(handles=legend_elements, loc="upper left", bbox_to_anchor=(-0.2, 1.0), fontsize=9)

    title_color = 'white' if is_night else 'green'
    ax.set_title(f"🪐 Sky View at {slider_time_ist.strftime('%Y-%m-%d %H:%M IST')}", 
                 fontsize=14, color=title_color, pad=30)

    st.pyplot(fig)
