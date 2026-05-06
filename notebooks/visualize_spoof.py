import numpy as np
import matplotlib.pyplot as plt

# Generate a "Real" Signal: A weak GPS sine wave buried in noise
t = np.linspace(0, 1, 1000)
noise = np.random.normal(0, 1, 1000)
gps_signal = 0.5 * np.sin(2 * np.pi * 5 * t)  # The real satellite
spoofer = 5.0 * np.sin(2 * np.pi * 5 * t)     # The powerful attacker

plt.figure(figsize=(10,4))
plt.plot(noise + gps_signal, label="Clean GNSS + Noise", alpha=0.7)
plt.plot(noise + spoofer, label="SPOOFED Signal (High Power)", color='red', alpha=0.5)
plt.title("Time-Domain Analysis: Real vs Spoofed")
plt.legend()
plt.savefig("../docs/signal_comparison.png") # Saves the evidence for your report
print("Visualization saved to docs/signal_comparison.png")