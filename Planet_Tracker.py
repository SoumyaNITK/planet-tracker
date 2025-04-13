import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from astropy.coordinates import EarthLocation, AltAz, get_body, get_sun
from astropy.time import Time
from astropy import units as u
import datetime

st.set_page_config(page_title="🌍 Planet Tracker", layout="wide")

st.title("🌍 Planet Tracker (India)")
st.markdown("See which planets and the Sun are visible in the sky above you.")

# Input location
col1, col2 = st.columns(2)
with col1:
    lat = st.number_input("Latitude (°)", value=13.00844, format="%.5f")
with col2:
    lon = st.number_input("Longitude (°)", value=74.79777, format="%.5f")

location = EarthLocation(lat=lat * u.deg, lon=lon * u.deg)

# Time input (default to current IST)
current_ist = datetime.datetime.utcnow() + datetime.timedelta(hours=5.5)
custom_time = st.time_input("Select time (IST)", value=current_ist.time())
custom_date = st.date_input("Select date", value=current_ist.date())

time_ist = datetime.datetime.combine(custom_date, custom_time)
time_utc = Time(time_ist - datetime.timedelta(hours=5.5))

altaz = AltAz(location=location, obstime=time_utc)

# Define planets and their colors
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

# Add visible celestial bodies
for planet, color in planets.items():
    if planet == "sun":
        obj = sun
    else:
        obj = get_body(planet, time_utc, location).transform_to(altaz)
    if obj.alt.degree > 0:
        altitudes.append(obj.alt.degree)
        azimuths.append(obj.az.degree)
        labels.append(planet.capitalize())
        colors.append(color)

plt.rcParams["font.family"] = "Segoe UI Emoji"

if not labels:
    st.warning(f"No planets or Sun visible above the horizon at {time_ist.strftime('%Y-%m-%d %H:%M IST')}.")
else:
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(10, 10))

    # Sky color based on day/night
    if is_night:
        ax.set_facecolor('#0a0a23')
        alpha = 1.0
    elif is_day:
        ax.set_facecolor('#e5e6ae')
        alpha = 0.3
    else:
        ax.set_facecolor('#2c7491')
        alpha = 0.6

    azimuths = np.radians(azimuths)
    altitudes = 90 - np.array(altitudes)

    sizes = [200 if label == "Sun" else 100 for label in labels]
    ax.scatter(azimuths, altitudes, c=colors, s=sizes, alpha=alpha)

    for i, txt in enumerate(labels):
        ax.text(azimuths[i], altitudes[i], txt, fontsize=12, ha='right', color=colors[i], alpha=alpha)

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
    ax.set_title(f"🌍 Planets & Sun at {time_ist.strftime('%Y-%m-%d %H:%M IST')}",
                 fontsize=14, color=title_color, pad=30)

    st.pyplot(fig)
