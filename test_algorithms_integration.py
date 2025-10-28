"""
Integration test for all algorithm endpoints
Tests time-domain, frequency-domain, and time-frequency analysis algorithms
"""
import requests
import json

BASE_URL = "http://localhost:8081"
BEARING_NAME = "Bearing1_1"
FILE_NUMBER = 1

def test_endpoint(name, url, expected_keys):
    """Test a single endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print(f"{'='*60}")

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Check for expected keys
        missing_keys = [key for key in expected_keys if key not in data]
        if missing_keys:
            print(f"❌ FAILED: Missing keys: {missing_keys}")
            return False

        print(f"✓ SUCCESS: All expected keys present")
        print(f"Response keys: {list(data.keys())}")

        # Print some sample data
        if 'horizontal' in data and 'vertical' in data:
            print(f"\nSample data:")
            print(f"  Horizontal: {json.dumps(data['horizontal'], indent=2)[:200]}...")
            print(f"  Vertical: {json.dumps(data['vertical'], indent=2)[:200]}...")

        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ FAILED: Request error - {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ FAILED: JSON decode error - {e}")
        return False
    except Exception as e:
        print(f"❌ FAILED: Unexpected error - {e}")
        return False


def main():
    """Run all algorithm tests"""
    print("\n" + "="*60)
    print("ALGORITHM INTEGRATION TEST SUITE")
    print("="*60)
    print(f"Testing bearing: {BEARING_NAME}, File: {FILE_NUMBER}")

    tests = [
        # Time Domain
        {
            "name": "Time Domain Features",
            "url": f"{BASE_URL}/api/algorithms/time-domain/{BEARING_NAME}/{FILE_NUMBER}",
            "expected_keys": ["bearing_name", "file_number", "data_points", "horizontal", "vertical", "signal_data"]
        },

        # Frequency Domain (FFT)
        {
            "name": "Frequency Domain (FFT)",
            "url": f"{BASE_URL}/api/algorithms/frequency-fft/{BEARING_NAME}/{FILE_NUMBER}",
            "expected_keys": ["bearing_name", "file_number", "sampling_rate", "horizontal", "vertical", "fft_spectrum"]
        },

        # Frequency Domain (TSA)
        {
            "name": "Frequency Domain (TSA)",
            "url": f"{BASE_URL}/api/algorithms/frequency-tsa/{BEARING_NAME}/{FILE_NUMBER}",
            "expected_keys": ["bearing_name", "file_number", "sampling_rate", "horizontal", "vertical", "tsa_spectrum"]
        },

        # Envelope Analysis
        {
            "name": "Envelope Spectrum",
            "url": f"{BASE_URL}/api/algorithms/envelope/{BEARING_NAME}/{FILE_NUMBER}",
            "expected_keys": ["bearing_name", "file_number", "filter_band", "horizontal", "vertical", "envelope_spectrum"]
        },

        # STFT
        {
            "name": "STFT (Short-Time Fourier Transform)",
            "url": f"{BASE_URL}/api/algorithms/stft/{BEARING_NAME}/{FILE_NUMBER}?window=hann",
            "expected_keys": ["bearing_name", "file_number", "sampling_rate", "window", "horizontal", "vertical", "spectrogram_data"]
        },

        # CWT
        {
            "name": "CWT (Continuous Wavelet Transform)",
            "url": f"{BASE_URL}/api/algorithms/cwt/{BEARING_NAME}/{FILE_NUMBER}?wavelet=morl",
            "expected_keys": ["bearing_name", "file_number", "sampling_rate", "wavelet", "horizontal", "vertical", "cwt_data"]
        },

        # Higher Order Statistics
        {
            "name": "Higher Order Statistics",
            "url": f"{BASE_URL}/api/algorithms/higher-order/{BEARING_NAME}/{FILE_NUMBER}",
            "expected_keys": ["bearing_name", "file_number", "data_points", "horizontal", "vertical"]
        },

        # Spectrogram
        {
            "name": "Spectrogram",
            "url": f"{BASE_URL}/api/algorithms/spectrogram/{BEARING_NAME}/{FILE_NUMBER}",
            "expected_keys": ["bearing_name", "file_number", "sampling_rate", "horizontal", "vertical", "spectrogram_data"]
        }
    ]

    results = []
    for test in tests:
        result = test_endpoint(test["name"], test["url"], test["expected_keys"])
        results.append((test["name"], result))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print(f"\n{'='*60}")
    print(f"Total: {passed}/{total} tests passed ({100*passed/total:.1f}%)")
    print(f"{'='*60}\n")

    return passed == total


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
