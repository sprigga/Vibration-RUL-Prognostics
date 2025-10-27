"""
Test script for time-frequency API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8081"

def test_stft():
    """Test STFT endpoint"""
    print("\n=== Testing STFT Endpoint ===")
    url = f"{BASE_URL}/api/algorithms/stft/Bearing1_1/1?window=hann"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ STFT calculation successful")
            print(f"  - Bearing: {data['bearing_name']}")
            print(f"  - File: {data['file_number']}")
            print(f"  - Horizontal NP4: {data['horizontal']['np4']:.4f}")
            print(f"  - Vertical NP4: {data['vertical']['np4']:.4f}")
            print(f"  - Horizontal Max Freq: {data['horizontal']['max_freq']:.2f} Hz")
            print(f"  - Vertical Max Freq: {data['vertical']['max_freq']:.2f} Hz")
        else:
            print(f"✗ STFT failed: {response.status_code}")
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"✗ STFT error: {str(e)}")


def test_cwt():
    """Test CWT endpoint"""
    print("\n=== Testing CWT Endpoint ===")
    url = f"{BASE_URL}/api/algorithms/cwt/Bearing1_1/1?wavelet=morl"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ CWT calculation successful")
            print(f"  - Bearing: {data['bearing_name']}")
            print(f"  - File: {data['file_number']}")
            print(f"  - Horizontal NP4: {data['horizontal']['np4']:.4f}")
            print(f"  - Vertical NP4: {data['vertical']['np4']:.4f}")
            print(f"  - Horizontal Max Scale: {data['horizontal']['max_scale']:.2f}")
            print(f"  - Horizontal Max Freq: {data['horizontal']['max_freq']:.2f} Hz")
        else:
            print(f"✗ CWT failed: {response.status_code}")
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"✗ CWT error: {str(e)}")


def test_higher_order():
    """Test Higher Order Statistics endpoint"""
    print("\n=== Testing Higher Order Statistics Endpoint ===")
    url = f"{BASE_URL}/api/algorithms/higher-order/Bearing1_1/1"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Higher Order Statistics calculation successful")
            print(f"  - Bearing: {data['bearing_name']}")
            print(f"  - File: {data['file_number']}")
            print(f"  - Horizontal NA4: {data['horizontal']['na4']:.4f}")
            print(f"  - Horizontal FM4: {data['horizontal']['fm4']:.4f}")
            print(f"  - Horizontal M6A: {data['horizontal']['m6a']:.6f}")
            print(f"  - Horizontal M8A: {data['horizontal']['m8a']:.8f}")
            print(f"  - Horizontal ER: {data['horizontal']['er']:.4f}")
        else:
            print(f"✗ Higher Order failed: {response.status_code}")
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"✗ Higher Order error: {str(e)}")


def test_spectrogram():
    """Test Spectrogram endpoint"""
    print("\n=== Testing Spectrogram Endpoint ===")
    url = f"{BASE_URL}/api/algorithms/spectrogram/Bearing1_1/1"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Spectrogram calculation successful")
            print(f"  - Bearing: {data['bearing_name']}")
            print(f"  - File: {data['file_number']}")
            print(f"  - Horizontal Mean Power: {data['horizontal']['mean_power']:.2f} dB")
            print(f"  - Horizontal Max Power: {data['horizontal']['max_power']:.2f} dB")
            print(f"  - Horizontal Peak Freq: {data['horizontal']['peak_freq']:.2f} Hz")
        else:
            print(f"✗ Spectrogram failed: {response.status_code}")
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"✗ Spectrogram error: {str(e)}")


def main():
    print("=" * 60)
    print("Time-Frequency Analysis API Tests")
    print("=" * 60)

    # Test all endpoints
    test_stft()
    test_cwt()
    test_higher_order()
    test_spectrogram()

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
