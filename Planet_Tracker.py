import numpy as np
import matplotlib.pyplot as plt
from astropy.coordinates import EarthLocation, AltAz, get_body, get_sun
from astropy.time import Time
from astropy import units as u
import streamlit as st

st.set_page_config(page_title="Planet Tracker 🌍", layout="wide")


location = EarthLocation(lat=13.00844*u.deg, lon=74.79777*u.deg)

time_utc = Time.now()
time_ist = time_utc + 5.5 * u.hour

altaz = AltAz(location=location, obstime=time_utc)

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
    print(f"No planets or Sun visible above the horizon at {time_ist.to_datetime().strftime('%Y-%m-%d %H:%M IST')}.")
else:
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(10, 10))

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
    scatter = ax.scatter(azimuths, altitudes, c=colors, s=sizes, alpha=alpha)

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
    ax.legend(handles=legend_elements, loc="upper left" , bbox_to_anchor=(-0.2, 1.0), fontsize=10)

    ax.grid(True, linestyle="--", alpha=0.6)
    title_color = 'white' if is_night else 'green'
    ax.set_title(f"🌍 Planets & Sun at {time_ist.to_datetime().strftime('%Y-%m-%d %H:%M IST')}", 
                 fontsize=14, color=title_color,pad=30)

    plt.show()
