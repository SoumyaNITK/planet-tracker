import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from astropy.coordinates import EarthLocation, AltAz, get_body, get_sun
from astropy.time import Time
from astropy import units as u
from datetime import datetime, timedelta

# App layout
st.set_page_config(page_title="Planet Tracker", layout="centered")
st.title("🌌 Planet Tracker")
st.markdown("Enter your location and choose a time to see visible planets in the sky.")

# Location input
latitude = st.number_input("Latitude (°)", value=0.0, format="%.5f")
longitude = st.number_input("Longitude (°)", value=0.0, format="%.5f")
location = EarthLocation(lat=latitude * u.deg, lon=longitude * u.deg)

# Time slider
now = datetime.utcnow()
slider_time = st.slider(
    "Select time (UTC)", 
    min_value=now.replace(hour=0, minute=0, second=0, microsecond=0),
    max_value=now.replace(hour=23, minute=59, second=0, microsecond=0),
    value=now,
    format="HH:mm"
)

time_utc = Time(slider_time)
time_ist = time_utc + 5.5 * u.hour
altaz = AltAz(location=location, obstime=time_utc)

# Planet colors
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

# Plotting
if not labels:
    st.warning(f"No visible planets/Sun at {time_ist.to_datetime().strftime('%Y-%m-%d %H:%M IST')}")
else:
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(8, 8))

    # Background based on time
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
    ax.grid(True, linestyle="--", alpha=0.6)

    from matplotlib.lines import Line2D
    legend_elements = [Line2D([0], [0], marker='o', color='w', label=labels[i],
                              markerfacecolor=colors[i], markersize=14 if labels[i] == "Sun" else 10)
                       for i in range(len(labels))]
    ax.legend(handles=legend_elements, loc="upper left", bbox_to_anchor=(-0.2, 1.0), fontsize=9)

    title_color = 'white' if is_night else 'green'
    ax.set_title(f"🕒 {time_ist.to_datetime().strftime('%Y-%m-%d %H:%M IST')}",
                 fontsize=14, color=title_color, pad=30)

    st.pyplot(fig)
