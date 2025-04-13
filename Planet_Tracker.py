import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from astropy.coordinates import EarthLocation, AltAz, get_body, get_sun
from astropy.time import Time
from astropy import units as u
from geopy.geocoders import Nominatim
from astroplan import Observer
import datetime
import re

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
    pass

# Show current IST time
current_ist = datetime.datetime.utcnow() + datetime.timedelta(hours=5.5)
st.markdown(f"**Current IST**: {current_ist.strftime('%Y-%m-%d %H:%M')}")

# Session state
if "date" not in st.session_state:
    st.session_state["date"] = current_ist.date()
if "time_input" not in st.session_state:
    st.session_state["time_input"] = current_ist.strftime("%H:%M")

# Inputs
date = st.date_input("Select date", value=st.session_state["date"])
time_input = st.text_input("Enter time (IST) in HH:MM format", value=st.session_state["time_input"])

# Validate time
time_valid = False
if re.match(r"^\d{2}:\d{2}$", time_input):
    try:
        time = datetime.datetime.strptime(time_input, "%H:%M").time()
        st.session_state["time_input"] = time_input
        time_valid = True
    except ValueError:
        st.warning("Invalid time! Use 24-hour format like 18:30.")
else:
    st.warning("Invalid format! Please enter time in HH:MM format.")

st.session_state["date"] = date

if time_valid:
    # UTC conversion
    time_ist = datetime.datetime.combine(date, time)
    time_utc = Time(time_ist - datetime.timedelta(hours=5.5))
    altaz = AltAz(location=location, obstime=time_utc)
    observer = Observer(location=location, timezone="Asia/Kolkata")

    # Planets
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
    rise_set_info = []

    sun = get_sun(time_utc).transform_to(altaz)
    is_night = sun.alt.degree < -6
    is_day = sun.alt.degree > 0

    for planet, color in planets.items():
        body = get_sun(time_utc) if planet == "sun" else get_body(planet, time_utc, location)
        body_altaz = body.transform_to(altaz)
        if body_altaz.alt.degree > 0:
            altitudes.append(body_altaz.alt.degree)
            azimuths.append(body_altaz.az.degree)
            labels.append(planet.capitalize())
            colors.append(color)

        # Rise/Set times
        try:
            rise_time = observer.target_rise_time(time_utc, body, which="next").to_datetime(timezone=datetime.timezone.utc) + datetime.timedelta(hours=5.5)
            set_time = observer.target_set_time(time_utc, body, which="next").to_datetime(timezone=datetime.timezone.utc) + datetime.timedelta(hours=5.5)
            rise_set_info.append((planet.capitalize(), rise_time.strftime("%H:%M"), set_time.strftime("%H:%M")))
        except:
            rise_set_info.append((planet.capitalize(), "—", "—"))

    # Plot
    plt.rcParams["font.family"] = "Segoe UI Emoji"
    if not labels:
        st.warning(f"No planets or Sun visible above the horizon at {time_ist.strftime('%Y-%m-%d %H:%M IST')}.")
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
        ax.set_title(f"Planets & Sun at {time_ist.strftime('%Y-%m-%d %H:%M IST')}",
                     fontsize=14, color='#041236', pad=30)
        st.pyplot(fig)

    # Rise/set table
    st.markdown("### 🌅 Rise and 🌇 Set Times (IST)")
    for name, rise, set_ in rise_set_info:
        st.markdown(f"**{name}**: 🌅 {rise} | 🌇 {set_}")
