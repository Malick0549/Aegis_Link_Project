import sys
import os

# This line allows the test to find your src folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from processing import calculate_trust_score

def test_spoofing_detection():
    print("Running Test: High Power Attack...")
    # Simulate a loud spoofer (-10dB is very strong/dangerous)
    score = calculate_trust_score(rssi=-10.0, constellation_count=1)
    assert score < 50, f"FAILED: System trusted a loud signal! Score: {score}"
    print("✅ PASSED: System correctly flagged the high-power signal.")

def test_safe_signal():
    print("Running Test: Normal Satellite Signal...")
    # Simulate a weak, healthy satellite signal
    score = calculate_trust_score(rssi=-40.0, constellation_count=3)
    assert score > 80, f"FAILED: System flagged a healthy signal! Score: {score}"
    print("✅ PASSED: System correctly trusted the healthy signal.")

if __name__ == "__main__":
    try:
        test_spoofing_detection()
        test_safe_signal()
        print("\n🏆 ALL CORE DEFENSES FUNCTIONAL")
    except AssertionError as e:
        print(f"\n❌ SECURITY GAP FOUND: {e}")