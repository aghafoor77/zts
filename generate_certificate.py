#!/usr/bin/env python3
"""
Generate Self-Signed Certificate for IoT Sensor
Creates a certificate in PEM format for sensor authentication
"""
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from datetime import datetime, timedelta
import os

def generate_self_signed_certificate(sensor_id="sensor_001"):
    """
    Generate a self-signed certificate for an IoT sensor
    
    Args:
        sensor_id: Unique identifier for the sensor
        
    Returns:
        tuple: (certificate_pem, private_key_pem)
    """
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # Create certificate subject
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "SE"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Stockholm"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Stockholm"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "IoT Sensors Inc"),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "IoT Devices"),
        x509.NameAttribute(NameOID.COMMON_NAME, f"iot-sensor-{sensor_id}"),
    ])
    
    # Create certificate
    certificate = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName(f"sensor-{sensor_id}.local"),
            x509.DNSName(f"{sensor_id}.iot.local"),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256())
    
    # Serialize certificate to PEM format
    cert_pem = certificate.public_bytes(serialization.Encoding.PEM).decode('utf-8')
    
    # Serialize private key to PEM format
    key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')
    
    return cert_pem, key_pem


if __name__ == "__main__":
    # Generate certificate for sensor_001
    cert_pem, key_pem = generate_self_signed_certificate("sensor_001")
    
    # Save to files
    os.makedirs("certs", exist_ok=True)
    
    with open("certs/sensor_001_cert.pem", "w") as f:
        f.write(cert_pem)
    
    with open("certs/sensor_001_key.pem", "w") as f:
        f.write(key_pem)
    
    print("Certificate generated successfully!")
    print("\n=== Certificate (PEM) ===")
    print(cert_pem)
    print("\n=== Private Key (PEM) ===")
    print(key_pem)
    
    # Print certificate as single-line string for code
    cert_oneline = cert_pem.replace('\n', '\\n')
    print("\n=== Certificate as single-line string ===")
    print(f'"{cert_oneline}"')

# Made with Bob