import numpy as np
import matplotlib.pyplot as plt
from astropy.coordinates import EarthLocation, AltAz, get_body, get_sun
from astropy.time import Time
from astropy import units as u
from matplotlib.lines import Line2D
import streamlit as st

st.set_page_config(page_title="Planet Tracker", layout="wide")
st.title("🌍 Planet Tracker")
st.markdown("### See which planets are visible from your location right now!")

# Sidebar for location input
st.sidebar.header("📍 Enter Your Location")

latitude = st.sidebar.number_input("Latitude (°)", value=13.00844, format="%.6f")
longitude = st.sidebar.number_input("Longitude (°)", value=74.79777, format="%.6f")

location = EarthLocation(lat=latitude * u.deg, lon=longitude * u.deg)


# Get current time
time_utc = Time.now()
time_ist = time_utc + 5.5 * u.hour
altaz = AltAz(location=location, obstime=time_utc)

# Define planets and colors
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

# Sun for visibility check
sun = get_sun(time_utc).transform_to(altaz)
is_night = sun.alt.degree < -6
is_day = sun.alt.degree > 0

# Track all visible bodies
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

# Plot if any are visible
if not labels:
    st.warning(f"No planets or Sun visible above the horizon at {time_ist.to_datetime().strftime('%Y-%m-%d %H:%M IST')}.")
else:
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(8, 8))

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
    ax.grid(True, linestyle="--", alpha=0.6)

    title_color = 'white' if is_night else 'green'
    ax.set_title(f"🌍 Planets & Sun at {time_ist.to_datetime().strftime('%Y-%m-%d %H:%M IST')}", fontsize=14, color=title_color, pad=30)

    legend_elements = [Line2D([0], [0], marker='o', color='w', label=labels[i],
                              markerfacecolor=colors[i], markersize=14 if labels[i] == "Sun" else 10)
                       for i in range(len(labels))]
    ax.legend(handles=legend_elements, loc="upper left", bbox_to_anchor=(-0.2, 1.0), fontsize=10)

    # Show in Streamlit
    st.pyplot(fig)
