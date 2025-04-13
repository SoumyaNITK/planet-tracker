import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from astropy.coordinates import EarthLocation, AltAz, get_body, get_sun
from astropy.time import Time
from astropy import units as u
from datetime import datetime, timedelta

# Page setup
st.set_page_config(page_title="🪐 Indian Planet Tracker", layout="centered")
st.title("🇮🇳 Indian Planet Tracker")
st.markdown("Track which planets are visible in the Indian sky at a given time.")

# --- Location Input (defaults to Bengaluru) ---
latitude = st.number_input("Your Latitude (°)", value=12.9716, format="%.5f")
longitude = st.number_input("Your Longitude (°)", value=77.5946, format="%.5f")
location = EarthLocation(lat=latitude * u.deg, lon=longitude * u.deg)

# --- Time Input (IST) ---
now_ist = datetime.utcnow() + timedelta(hours=5, minutes=30)
slider_time_ist = st.slider(
    "Select Time (IST)",
    min_value=now_ist.replace(hour=0, minute=0, second=0, microsecond=0),
    max_value=now_ist.replace(hour=23, minute=59, second=0, microsecond=0),
    value=now_ist,
    step=timedelta(minutes=30),
    format="HH:mm"
)

# Convert IST to UTC
slider_time_utc = slider_time_ist - timedelta(hours=5, minutes=30)
time_utc = Time(slider_time_utc)
altaz = AltAz(location=location, obstime=time_utc)

# --- Planet Info ---
planets = {
    "Mercury": "blue",
    "Venus": "orange",
    "Mars": "red",
    "Jupiter": "green",
    "Saturn": "purple",
    "Uranus": "cyan",
    "Neptune": "navy",
    "Sun": "yellow"
}

altitudes = []
azimuths = []
labels = []
colors = []

sun = get_sun(time_utc).transform_to(altaz)
is_night = sun.alt < -6 * u.deg
is_day = sun.alt > 0 * u.deg

for name, color in planets.items():
    obj = get_sun(time_utc) if name == "Sun" else get_body(name.lower(), time_utc, location)
    obj_altaz = obj.transform_to(altaz)
    if obj_altaz.alt > 0 * u.deg:
        altitudes.append(obj_altaz.alt.degree)
        azimuths.append(obj_altaz.az.degree)
        labels.append(name)
        colors.append(color)

# --- Plotting ---
if not labels:
    st.warning(f"No visible planets/Sun at {slider_time_ist.strftime('%Y-%m-%d %H:%M IST')}")
else:
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(8, 8))

    if is_night:
        ax.set_facecolor("#0a0a23")  # Night
        alpha = 1.0
    elif is_day:
        ax.set_facecolor("#ffffe0")  # Day
        alpha = 0.3
    else:
        ax.set_facecolor("#2c7491")  # Twilight
        alpha = 0.6

    azimuths_rad = np.radians(azimuths)
    altitudes_inverted = 90 - np.array(altitudes)
    sizes = [200 if label == "Sun" else 100 for label in labels]

    ax.scatter(azimuths_rad, altitudes_inverted, c=colors, s=sizes, alpha=alpha)

    for i, name in enumerate(labels):
        ax.text(azimuths_rad[i], altitudes_inverted[i], name, fontsize=12, ha='right', color=colors[i], alpha=alpha)

    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_rmax(90)
    ax.set_rticks([30, 60, 90])
    ax.set_xticks(np.radians([0, 90, 180, 270]))
    ax.set_xticklabels(["N", "E", "S", "W"])
    ax.grid(True, linestyle="--", alpha=0.6)

    st.pyplot(fig)

    st.info(f"🕒 {slider_time_ist.strftime('%Y-%m-%d %H:%M IST')} | 🌓 {'Night' if is_night else 'Day' if is_day else 'Twilight'}")
