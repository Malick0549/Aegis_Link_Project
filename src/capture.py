import numpy as np
import time

def get_warzone_signal():
    """
    Simulates the 'Electronic Fog' of the 2026 conflict.
    Returns a realistic RSSI value based on distance from a jammer.
    """
    # Base noise level
    base_signal = -45.0 
    
    # Simulate a jamming drone passing by (Power spikes randomly)
    interference = np.random.normal(0, 5) 
    
    # Occasional "State-Level" Spoofing spike
    if np.random.random() > 0.8:
        interference += 30 # Huge jump in power
        
    return base_signal + interference

def get_recorded_nmea_data():
    """Reads the actual NMEA evidence log from the data folder."""
    try:
        with open("data/spoofing_log_2026.nmea", "r") as f:
            lines = f.readlines()
            # Return a random line to simulate a 'stream'
            import random
            return random.choice(lines)
    except FileNotFoundError:
        return "$GPGSV,1,1,01,21,12,122,44*41" # Fallback

if __name__ == "__main__":
    print(f"Test Signal: {get_warzone_signal()} dB")