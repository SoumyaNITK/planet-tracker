import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from astropy.coordinates import EarthLocation, AltAz, get_body, get_sun
from astropy.time import Time
from astropy import units as u
from geopy.geocoders import Nominatim
import datetime
import re
from astroplan import Observer, FixedTarget
from astropy.coordinates import solar_system_ephemeris

st.set_page_config(page_title="🌍 Planet Tracker by Soumya", layout="wide")
st.title("🌍 Planet Tracker by Soumya")
st.markdown("See which planets and the Sun are visible in the sky above you.")

# Location input
col1, col2 = st.columns(2)
with col1:
    lat = st.number_input("Latitude (°)", value=13.00844, format="%.5f")
with col2:
    lon = st.number_input("Longitude (°)", value=74.79777, format="%.5f")

location = EarthLocation(lat=lat * u.deg, lon=lon * u.deg)

# Show location name using geopy
try:
    geolocator = Nominatim(user_agent="planet_tracker")
    location_name = geolocator.reverse((lat, lon), language="en")
    if location_name:
        st.markdown(f"**Location**: {location_name.address}")
except Exception:
    pass  # If geopy fails, continue silently

# Show current IST time
current_ist = datetime.datetime.utcnow() + datetime.timedelta(hours=5.5)
st.markdown(f"**Current IST**: {current_ist.strftime('%Y-%m-%d %H:%M')}")

# Initialize session state for time
if "time_input" not in st.session_state:
    current_time_str = current_ist.strftime("%H:%M")
    st.session_state.time_input = current_time_str
    st.session_state.time = datetime.datetime.strptime(current_time_str, "%H:%M").time()

# Date input
date = st.date_input("Select date", value=st.session_state.get('date', current_ist.date()))
st.session_state.date = date

# Time input
time_input = st.text_input("Enter time (IST) in HH:MM format", key="time_input")

# Time validation
if re.match(r"^\d{2}:\d{2}$", time_input.strip()):
    try:
        parsed_time = datetime.datetime.strptime(time_input.strip(), "%H:%M").time()
        st.session_state.time = parsed_time
    except ValueError:
        st.warning("Invalid time! Use 24-hour format like 18:30.")
else:
    st.warning("Invalid format! Please enter time in HH:MM format.")

# Convert to UTC
time_ist = datetime.datetime.combine(st.session_state.date, st.session_state.time)
time_utc = Time(time_ist - datetime.timedelta(hours=5.5))
altaz = AltAz(location=location, obstime=time_utc)

# Planets and colors
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

plt.rcParams["font.family"] = "Segoe UI Emoji"

if not labels:
    st.warning(f"No planets or Sun visible above the horizon at {time_ist.strftime('%Y-%m-%d %H:%M IST')}.")
else:
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(10, 10))

    if is_night:
        ax.set_facecolor('#0a0a23')
        alpha = 1.0
    elif is_day:
        ax.set_facecolor('#b5d0e8')
        alpha = 0.3
    else:
        ax.set_facecolor('#d4727e')
        alpha = 0.6

    azimuths_rad = np.radians(azimuths)
    altitudes_transformed = 90 - np.array(altitudes)

    sizes = [200 if label == "Sun" else 100 for label in labels]
    ax.scatter(azimuths_rad, altitudes_transformed, c=colors, s=sizes, alpha=alpha)

    for i, txt in enumerate(labels):
        ax.text(azimuths_rad[i], altitudes_transformed[i], txt, fontsize=12, ha='right', color=colors[i], alpha=alpha)

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
    title_color = '#041236'
    ax.set_title(f"Planets & Sun at {time_ist.strftime('%Y-%m-%d %H:%M IST')}",
                 fontsize=14, color=title_color, pad=30)

    st.pyplot(fig)

# Rise and Set Times
st.markdown("---")
st.subheader("🌅 Planet Rise and Set Times")

observer = Observer(location=location, timezone="Asia/Kolkata")
target_time = time_utc

rise_set_info = []

with solar_system_ephemeris.set('builtin'):
    for planet in planets.keys():
        body = get_sun(target_time) if planet == "sun" else get_body(planet, target_time, location)
        target = FixedTarget(name=planet.capitalize(), coord=body)
        try:
            rise_time = observer.target_rise_time(target_time, target, which='next').to_datetime(timezone=observer.timezone)
            set_time = observer.target_set_time(target_time, target, which='next').to_datetime(timezone=observer.timezone)
            rise_str = rise_time.strftime("%H:%M")
            set_str = set_time.strftime("%H:%M")
        except:
            rise_str = "Never rises"
            set_str = "Never sets"
        rise_set_info.append((planet.capitalize(), rise_str, set_str))

# Display as table
st.table({
    "Planet": [x[0] for x in rise_set_info],
    "Rise (IST)": [x[1] for x in rise_set_info],
    "Set (IST)": [x[2] for x in rise_set_info],
})
