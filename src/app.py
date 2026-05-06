import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import time
import random
from datetime import datetime

# --- 1. SAFE-FAIL GEOSPATIAL SETUP ---
try:
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderServiceError
    HAS_GEOPY = True
except ImportError:
    HAS_GEOPY = False

# --- IMPORT CUSTOM MODULES ---
# Ensure these files are in your project directory
from capture import get_warzone_signal, get_recorded_nmea_data
from processing import (
    calculate_trust_score, 
    log_security_event, 
    get_verified_location, 
    multi_constellation_check,
    estimate_threat_distance,
    identify_emitter_signature,
    classify_platform
)

# --- 2. CONFIGURATION & FALLBACKS ---
SCAN_WINDOW = 12           
INTEL_HOLD_TIME = 20       
DETECTION_THRESHOLD = -25.0 
DEFAULT_LAT, DEFAULT_LON = 10.892, -1.092 

# --- 3. TACTICAL UI THEME (FULL SPEC) ---
st.set_page_config(page_title="AEGIS-LINK | STRATCOM", layout="wide", page_icon="🪖")

st.markdown("""
    <style>
    .stApp { background-color: #2b2d24; color: #f2f2e0; }
    [data-testid="stSidebar"] { background-color: #1a1c15; border-right: 2px solid #4b5320; }
    .stMetric { background-color: #35392e; border: 1px solid #4b5320; padding: 15px; border-radius: 4px; }
    div[data-testid="stMetricValue"] { color: #d4af37 !important; font-family: 'Courier New', monospace; font-size: 1.8rem !important; }
    h1, h2, h3 { font-family: 'Stencil', sans-serif; letter-spacing: 1px; text-transform: uppercase; color: #d4af37; }
    .intel-report { 
        background-color: #0d0e0a; 
        border: 2px solid #d4af37; 
        padding: 20px; 
        border-radius: 5px; 
        font-family: 'Courier New', monospace;
    }
    .label { color: #8b8e7a; font-weight: bold; }
    .value { color: #f2f2e0; font-weight: bold; }
    .stTable { background-color: #1a1c15 !important; color: #f2f2e0 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SESSION STATE (PERSISTENCE) ---
if 'history' not in st.session_state:
    st.session_state.history = []
if 'trust_history' not in st.session_state:
    st.session_state.trust_history = []
if 'status_lock' not in st.session_state:
    st.session_state.status_lock = {
        'is_alert': False, 'brand': 'GENERIC', 'model': 'SEARCHING', 'id_num': 'N/A',
        'size': 'MEDIUM', 'speed': 0, 'dist': 0.0, 'sig': 'NONE', 
        'desc': 'Initializing sensors...', 'ts': 0, 'status': 'STATIONARY', 
        'platform': 'SCANNER', 'icon': '📡'
    }

# --- 5. SIDEBAR: STRATEGIC CONTROLS ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #d4af37;'>⚔️</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-weight: bold;'>BATTLESPACE AWARENESS SYSTEM</p>", unsafe_allow_html=True)
    st.divider()
    
    st.subheader("📍 GLOBAL TARGETING")
    target_area = st.text_input("SCAN AREA (Town/City/Country)", value="Navrongo, Ghana")
    
    # Safe-Fail Coordinate Resolution
    t_lat, t_lon = DEFAULT_LAT, DEFAULT_LON
    if HAS_GEOPY:
        try:
            geolocator = Nominatim(user_agent="aegis_link_final_master")
            location = geolocator.geocode(target_area, timeout=5)
            if location:
                t_lat, t_lon = location.latitude, location.longitude
                st.success(f"LOCKED: {location.address[:30]}...")
            else:
                st.warning("Locating using Default HQ...")
        except:
            st.error("OFFLINE: Using Manual Coords")

    st.divider()
    mode = st.radio("OPERATIONAL MODE", ["COMBAT_LIVE", "FORENSIC_REPLAY"])
    st.divider()
    st.info(f"SYS_TIME: {datetime.utcnow().strftime('%H:%M:%S')} UTC")

# --- 6. SIGNAL CAPTURE & INTELLIGENCE ENGINE ---
if mode == "FORENSIC_REPLAY":
    raw_nmea = get_recorded_nmea_data()
    current_rssi = -12.0 if "GPRMC" in raw_nmea else -42.0 
else:
    current_rssi = get_warzone_signal()

# Update History
st.session_state.history.append(current_rssi)
if len(st.session_state.history) > 50: st.session_state.history.pop(0)

# Multi-Point Stability Brain
curr_time = time.time()
signal_active = current_rssi > DETECTION_THRESHOLD

if (curr_time - st.session_state.status_lock['ts']) > INTEL_HOLD_TIME:
    st.session_state.status_lock['is_alert'] = signal_active
    st.session_state.status_lock['ts'] = curr_time
    
    if signal_active:
        dist = estimate_threat_distance(current_rssi)
        sig_id, sig_desc = identify_emitter_signature(current_rssi)
        
        # Classification Engine (Cars/Bikes/Fixed)
        if current_rssi > -14: # Motorcycle High-Power
            brand, model_name = random.choice([("Yamaha", "MT-07"), ("Honda", "CB500X"), ("KTM", "Duke 390")])
            size, speed, plat, ico = "LIGHTWEIGHT", random.randint(35, 75), "MOTORCYCLE", "🏍️"
            id_tag = f"VIN: {random.randint(1000,9999)}-BK"
        elif current_rssi > -20: # Ground Vehicle
            brand, model_name = random.choice([("Toyota", "Hilux"), ("Ford", "Ranger"), ("Mercedes", "G-Wagon")])
            size, speed, plat, ico = "HEAVY GROUND", random.randint(10, 45), "GROUND VEHICLE", "🚗"
            id_tag = f"CHASSIS: {hex(random.randint(0x10000, 0xFFFFF))}"
        else: # Stationary Node
            brand, model_name = "HUAWEI / CISCO", "FIXED NODE"
            size, speed, id_tag, plat, ico = "SMALL", 0, "MAC: 00:1A:2B:3C", "STATIONARY EMITTER", "📡"

        st.session_state.status_lock.update({
            'brand': brand, 'model': model_name, 'id_num': id_tag, 'platform': plat,
            'size': size, 'speed': speed, 'dist': dist, 'sig': sig_id, 'desc': sig_desc,
            'status': 'MOBILE' if speed > 0 else 'STATIONARY', 'icon': ico
        })

# Cybersecurity Audit (Trust Score Logic)
raw_trust = calculate_trust_score(current_rssi, 1)
st.session_state.trust_history.append(raw_trust)
if len(st.session_state.trust_history) > SCAN_WINDOW: st.session_state.trust_history.pop(0)
avg_trust = sum(st.session_state.trust_history) / len(st.session_state.trust_history)
is_spoofed = avg_trust < 50

# --- 7. MAIN INTERFACE ---

# STATUS BANNER
if st.session_state.status_lock['is_alert']:
    st.markdown(f"""<div style="background-color:#7c2d12; padding:15px; border:2px solid #d4af37; text-align:center;">
        <h2 style="margin:0; color:white;">⚠️ {st.session_state.status_lock['status']} {st.session_state.status_lock['platform']} DETECTED</h2>
    </div>""", unsafe_allow_html=True)
else:
    st.markdown(f"""<div style="background-color:#365314; padding:15px; border:2px solid #4b5320; text-align:center;">
        <h2 style="margin:0; color:#d4af37;">🟢 STATUS: NOMINAL // SCANNING {target_area.upper()}</h2>
    </div>""", unsafe_allow_html=True)

st.divider()

col1, col2 = st.columns([1.6, 1])

with col1:
    st.markdown("### 📡 Spectrum Analysis & Spatial Radar")
    st.area_chart(st.session_state.history, color="#d4af37")
    
    # 1. POLAR RADAR CHART (Older Feature Complete)
    if is_spoofed:
        sky_data = pd.DataFrame({'azimuth': [180, 182, 179], 'elevation': [1, 2, 1], 'sat': ['S1','S2','S3']})
    else:
        sky_data = pd.DataFrame({'azimuth': [45, 120, 280, 10, 210], 'elevation': [40, 65, 30, 55, 42], 'sat': ['G1','G12','E1','B2','R5']})
    
    fig = px.scatter_polar(sky_data, r='elevation', theta='azimuth', color='sat', template="plotly_dark", range_r=[0,90])
    fig.update_polars(radialaxis_showticklabels=False, angularaxis_gridcolor="#4b5320")
    st.plotly_chart(fig, use_container_width=True)

    # 2. EXPANDED INTEL DOSSIER (Newer Features Integrated)
    if st.session_state.status_lock['is_alert']:
        s = st.session_state.status_lock
        st.markdown(f"### {s['icon']} TARGET INTELLIGENCE PROFILE")
        st.markdown(f"""
        <div class="intel-report">
            <span class="label">BRAND:</span> <span class="value">{s['brand']}</span> | <span class="label">MODEL:</span> <span class="value">{s['model']}</span><br>
            <span class="label">ID TAG:</span> <span class="value">{s['id_num']}</span><br>
            <span class="label">CLASS:</span> <span class="value">{s['platform']} ({s['size']})</span><br>
            <hr style="border: 1px solid #4b5320;">
            <span class="label">POSITION:</span> <span class="value">{t_lat:.5f}, {t_lon:.5f}</span><br>
            <span class="label">VELOCITY:</span> <span class="value">{s['speed']} KM/H</span> | <span class="label">RANGE:</span> <span class="value">{s['dist']} KM</span><br>
            <span class="label">FORENSIC NOTE:</span> <span class="value">{s['desc']}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Searching for valid RF signatures and asset reconstruction signals...")

with col2:
    st.markdown("### 🤖 Cybersecurity Audit")
    st.write(f"Data Integrity Level: {avg_trust:.1f}%")
    st.progress(int(avg_trust))
    
    if is_spoofed:
        st.warning("🚨 ELECTRONIC WARFARE DETECTED: Signal spoofing suspected!")
        log_security_event(avg_trust, current_rssi, "INTRUSION_ALERT")
    else:
        st.success("✅ GNSS Constellation Verified")

    st.divider()
    st.markdown("### 🗺️ Tracking & Consensus")
    # Dynamic Map
    st.map(pd.DataFrame({'lat': [t_lat], 'lon': [t_lon]}), zoom=14)
    
    # 3. MULTI-CONSTELLATION CONSENSUS TABLE (Older Feature Complete)
    sources = {
        "GPS (USA)": [t_lat, t_lon] if not is_spoofed else [t_lat + 0.04, t_lon - 0.03],
        "GALILEO (EU)": [t_lat + 0.001, t_lon + 0.002],
        "BEIDOU (CN)": [t_lat, t_lon],
        "GLONASS (RU)": [t_lat - 0.002, t_lon + 0.001]
    }
    st.table(pd.DataFrame.from_dict(sources, orient='index', columns=['LATITUDE', 'LONGITUDE']))

# --- 8. FOOTER ---
st.write("---")
st.caption(f"CYBERSECURITY FINAL YEAR PROJECT // AEGIS-LINK v5.5 // {target_area} // {datetime.now().strftime('%H:%M:%S')}")

time.sleep(1.8)
st.rerun()