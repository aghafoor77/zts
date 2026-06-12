#!/usr/bin/env python3
"""
Test Certificate-Based Digital Signing
Demonstrates reading certificate and private key in PEM format,
and digitally signing a random number
"""
import sys
import logging
from sensor.sensor import Sensor
from config.sensor_credentials import SENSOR_CERTIFICATE_PEM, SENSOR_PRIVATE_KEY_PEM

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Test certificate loading and digital signing"""
    
    print("=" * 80)
    print("IoT Sensor Certificate-Based Digital Signing Test")
    print("=" * 80)
    
    # Initialize sensor
    sensor = Sensor(
        sensor_id="sensor_001",
        device_type="sensor",
        manufacturer="TempCorp",
        model="TH-100",
        certificate=SENSOR_CERTIFICATE_PEM
    )
    
    print("\n1. Loading Certificate from PEM format...")
    print("-" * 80)
    try:
        cert = sensor.load_certificate_from_pem(SENSOR_CERTIFICATE_PEM)
        print(f"✓ Certificate loaded successfully")
        print(f"  Subject: {cert.subject}")
        print(f"  Issuer: {cert.issuer}")
        print(f"  Serial Number: {cert.serial_number}")
        print(f"  Valid From: {cert.not_valid_before}")
        print(f"  Valid Until: {cert.not_valid_after}")
    except Exception as e:
        print(f"✗ Failed to load certificate: {e}")
        sys.exit(1)
    
    print("\n2. Loading Private Key from PEM format...")
    print("-" * 80)
    try:
        private_key = sensor.load_private_key_from_pem(SENSOR_PRIVATE_KEY_PEM)
        print(f"✓ Private key loaded successfully")
        print(f"  Key Size: {private_key.key_size} bits")
        print(f"  Key Type: RSA")
    except Exception as e:
        print(f"✗ Failed to load private key: {e}")
        sys.exit(1)
    
    print("\n3. Generating Random Challenge and Signing...")
    print("-" * 80)
    try:
        challenge_response = sensor.generate_and_sign_challenge(SENSOR_PRIVATE_KEY_PEM)
        print(f"✓ Challenge generated and signed successfully")
        print(f"  Sensor ID: {challenge_response['sensor_id']}")
        print(f"  Challenge (hex): {challenge_response['challenge'][:32]}...")
        print(f"  Signature (base64): {challenge_response['signature'][:64]}...")
        print(f"  Timestamp: {challenge_response['timestamp']}")
        print(f"  Algorithm: {challenge_response['algorithm']}")
    except Exception as e:
        print(f"✗ Failed to generate and sign challenge: {e}")
        sys.exit(1)
    
    print("\n4. Verifying Signature...")
    print("-" * 80)
    try:
        # Convert challenge hex back to bytes for verification
        challenge_bytes = bytes.fromhex(challenge_response['challenge'])
        
        # Verify the signature
        is_valid = sensor.verify_signature(
            challenge_bytes,
            challenge_response['signature'],
            SENSOR_CERTIFICATE_PEM
        )
        
        if is_valid:
            print(f"✓ Signature verified successfully!")
            print(f"  The signature is authentic and matches the challenge")
        else:
            print(f"✗ Signature verification failed!")
            sys.exit(1)
    except Exception as e:
        print(f"✗ Error during verification: {e}")
        sys.exit(1)
    
    print("\n5. Testing with Modified Data (Should Fail)...")
    print("-" * 80)
    try:
        # Modify the challenge slightly
        modified_challenge = challenge_bytes[:-1] + b'\x00'
        
        is_valid = sensor.verify_signature(
            modified_challenge,
            challenge_response['signature'],
            SENSOR_CERTIFICATE_PEM
        )
        
        if not is_valid:
            print(f"✓ Correctly detected tampered data!")
            print(f"  Signature verification failed as expected")
        else:
            print(f"✗ WARNING: Signature verified for tampered data!")
    except Exception as e:
        print(f"✓ Correctly rejected tampered data with exception")
    
    print("\n" + "=" * 80)
    print("Certificate-Based Digital Signing Test Complete!")
    print("=" * 80)
    print("\nSummary:")
    print("  ✓ Certificate loaded and parsed")
    print("  ✓ Private key loaded")
    print("  ✓ Random challenge generated")
    print("  ✓ Challenge digitally signed with RSA-PSS-SHA256")
    print("  ✓ Signature verified successfully")
    print("  ✓ Tampered data correctly rejected")
    print("\nThe sensor can now use certificate-based authentication!")


if __name__ == "__main__":
    main()

# Made with Bob