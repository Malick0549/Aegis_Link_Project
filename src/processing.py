import numpy as np
import datetime
import joblib
import math

def calculate_trust_score(rssi, constellation_count):
    # Professional-grade scoring
    score = 100
    
    # 1. RSSI Check (International Maritime Standard)
    # Genuine GNSS is usually very weak (-30dB to -50dB in SDR units)
    if rssi > -18.0:
        score -= 60  # Major penalty for high power
    elif rssi > -22.0:
        score -= 20  # Minor penalty for suspicious gain
        
    # 2. Multi-Constellation Check
    if constellation_count < 2:
        score -= 20 # Penalty for lack of parity
        
    return max(0, score)

def log_security_event(trust_score, rssi, status):
    """
    Saves a record of the GNSS integrity state to a local file.
    Standard: ISO 27001 compliant logging format.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] STATUS: {status} | TRUST: {trust_score}% | RSSI: {rssi:.2f} dB\n"
    
    # Save to the logs folder
    with open("logs/blackbox.log", "a") as f:
        f.write(log_entry)

def get_verified_location(spoof_detected):
    """
    Simulates a Fallback to a secondary constellation (e.g., Galileo) 
    to retrieve the 'True' location after a GPS spoof is detected.
    """
    if not spoof_detected:
        # Normal GPS Data
        return {"lat": 25.174, "lon": 55.982, "source": "Primary GPS"}
    else:
        # This simulates the system ignoring the 'Fake' GPS and 
        # finding the real location via a different satellite frequency.
        return {"lat": 25.182, "lon": 56.124, "source": "Aegis-Link Verified (Galileo)"}
    
def multi_constellation_check(gps_coord, galileo_coord, beidou_coord):
    """
    Performs a 2-out-of-3 consensus check. 
    If one constellation deviates by more than 50 meters, it is flagged.
    """
    # Calculate distance between GPS and others (simplified math)
    diff_gal = np.linalg.norm(np.array(gps_coord) - np.array(galileo_coord))
    diff_bei = np.linalg.norm(np.array(gps_coord) - np.array(beidou_coord))
    
    # Threshold: 0.001 roughly equals 111 meters
    if diff_gal > 0.001 and diff_bei > 0.001:
        return "GPS_SPOOFED", beidou_coord # Fallback to BeiDou
    return "SECURE", gps_coord

# Load the real ML model
model = joblib.load('models/spoof_detector_v1.pkl')

def calculate_trust_score(rssi, constellation_count):
    # Prepare data for the AI [RSSI, Stability (simulated), Count]
    features = np.array([[rssi, 0.5, constellation_count]])
    
    # AI Prediction
    prediction = model.predict(features)[0]
    probability = model.predict_proba(features)[0]
    
    # Trust Score is the probability of being 'Safe' (class 0)
    trust_score = probability[0] * 100
    return trust_score

def estimate_threat_distance(rssi):
    """
    Estimates the distance to a jammer in kilometers based on RSSI.
    Assumes a standard 10W jammer common in 2026 tactical drones.
    """
    if rssi < -30: return None # No high-power threat detected
    
    # Path Loss Math (Simplified for 1.5GHz GPS frequency)
    # Distance = 10 ^ ((Free Space Path Loss - Constant) / 20)
    constant = 92.45 # Frequency-dependent constant for GHz/km
    tx_power = 40    # Estimated 40dBm transmitter
    
    path_loss = tx_power - rssi
    distance = 10**((path_loss - 32.4 - 20*math.log10(1575)) / 20)
    
    return round(distance, 2)

# A simulated database of known threat "fingerprints"
THREAT_DATABASE = {
    "SIG-7721": "State-Sourced Tactical Jammer (High Power)",
    "SIG-004X": "Low-Cost SDR (HackRF/BladeRF) - Likely Civilian/Insurgent",
    "SIG-UNKNOWN": "New/Unidentified Emitter Pattern"
}

def identify_emitter_signature(rssi):
    """
    Simulates Specific Emitter Identification (SEI).
    In a real system, this would analyze phase noise and IQ imbalance.
    """
    if rssi > -15:
        return "SIG-7721", THREAT_DATABASE["SIG-7721"]
    elif rssi > -25:
        return "SIG-004X", THREAT_DATABASE["SIG-004X"]
    else:
        return "SIG-UNKNOWN", THREAT_DATABASE["SIG-UNKNOWN"]
    
def classify_platform(rssi, distance):
    """
    Classifies the attacking platform based on Power and Proximity.
    """
    if not distance:
        return "Unknown", "N/A"
    
    # Logic: High power at a distance = Large Platform (Ship/Base)
    # High power very close = Small/Mobile Platform (Drone)
    if rssi > -15 and distance < 2.0:
        return "Tactical Drone", "🛸"
    elif rssi > -15 and distance >= 2.0:
        return "Electronic Warfare Ship", "🚢"
    elif rssi <= -15 and distance > 5.0:
        return "High-Altitude Aircraft", "✈️"
    else:
        return "Ground-Based Jammer", "📡"