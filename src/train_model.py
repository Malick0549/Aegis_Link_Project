from sklearn.ensemble import RandomForestClassifier
import joblib
import numpy as np

# Data: [RSSI, Signal_Stability, Satellite_Count]
# 1 = Spoofed, 0 = Safe
X = np.array([
    [-45, 0.9, 8], [-42, 0.8, 10],  # Safe
    [-10, 0.1, 1], [-5, 0.2, 2],    # Spoofed (High power, low count)
    [-30, 0.5, 4]                   # Uncertain
])
y = np.array([0, 0, 1, 1, 1])

model = RandomForestClassifier()
model.fit(X, y)

# Save the real "Brain"
joblib.dump(model, 'models/spoof_detector_v1.pkl')
print("Real Machine Learning Model saved to models/spoof_detector_v1.pkl")