# Aegis-Link Technical Specification
**Version:** 1.0 (May 2026)
**Standard:** Maritime Cyber-Resilience ISO/IEC 27001

## 1. Detection Methodology
We utilize **Receiver Autonomous Integrity Monitoring (RAIM)**. The system calculates the distance between the primary GNSS solution and secondary constellations (Galileo/BeiDou).

## 2. Thresholds
- **Critical Power (Pc):** > -18 dB
- **Geometric Anomaly:** Elevation < 5° for all visible SVs (Space Vehicles).

## 3. Mitigation
Upon detection, the NMEA stream is diverted to the **Consensus Engine**, which discards the spoofed packets.
