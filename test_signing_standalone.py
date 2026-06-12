#!/usr/bin/env python3
"""
Standalone Test for Certificate-Based Digital Signing
Demonstrates reading certificate and private key in PEM format,
and digitally signing a random number
"""
import secrets
import base64
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from config.sensor_credentials import SENSOR_CERTIFICATE_PEM, SENSOR_PRIVATE_KEY_PEM


def load_certificate_from_pem(pem_data: str) -> x509.Certificate:
    """Load X.509 certificate from PEM format string"""
    cert = x509.load_pem_x509_certificate(
        pem_data.encode('utf-8'),
        default_backend()
    )
    return cert


def load_private_key_from_pem(pem_data: str):
    """Load RSA private key from PEM format string"""
    private_key = serialization.load_pem_private_key(
        pem_data.encode('utf-8'),
        password=None,
        backend=default_backend()
    )
    return private_key


def sign_data(data: bytes, private_key) -> str:
    """Digitally sign data using RSA private key with SHA-256"""
    signature = private_key.sign(
        data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode('utf-8')


def verify_signature(data: bytes, signature_b64: str, public_key) -> bool:
    """Verify digital signature using public key"""
    try:
        signature = base64.b64decode(signature_b64)
        public_key.verify(
            signature,
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False


def main():
    """Test certificate loading and digital signing"""
    
    print("=" * 80)
    print("IoT Sensor Certificate-Based Digital Signing Test")
    print("=" * 80)
    
    # 1. Load Certificate
    print("\n1. Loading Certificate from PEM format...")
    print("-" * 80)
    cert = load_certificate_from_pem(SENSOR_CERTIFICATE_PEM)
    print(f"✓ Certificate loaded successfully")
    print(f"  Subject: {cert.subject}")
    print(f"  Issuer: {cert.issuer}")
    print(f"  Serial Number: {cert.serial_number}")
    print(f"  Valid From: {cert.not_valid_before}")
    print(f"  Valid Until: {cert.not_valid_after}")
    
    # 2. Load Private Key
    print("\n2. Loading Private Key from PEM format...")
    print("-" * 80)
    private_key = load_private_key_from_pem(SENSOR_PRIVATE_KEY_PEM)
    print(f"✓ Private key loaded successfully")
    print(f"  Key Size: {private_key.key_size} bits")
    print(f"  Key Type: RSA")
    
    # 3. Generate Random Challenge
    print("\n3. Generating Random Challenge Number...")
    print("-" * 80)
    challenge = secrets.token_bytes(32)  # 256-bit random number
    challenge_hex = challenge.hex()
    print(f"✓ Random challenge generated")
    print(f"  Challenge (hex): {challenge_hex}")
    print(f"  Challenge (bytes): {len(challenge)} bytes")
    
    # 4. Sign the Challenge
    print("\n4. Digitally Signing the Challenge...")
    print("-" * 80)
    signature = sign_data(challenge, private_key)
    print(f"✓ Challenge signed successfully")
    print(f"  Signature (base64): {signature[:64]}...")
    print(f"  Signature length: {len(signature)} characters")
    print(f"  Algorithm: RSA-PSS with SHA-256")
    
    # 5. Verify Signature
    print("\n5. Verifying Signature with Certificate's Public Key...")
    print("-" * 80)
    public_key = cert.public_key()
    is_valid = verify_signature(challenge, signature, public_key)
    
    if is_valid:
        print(f"✓ Signature verified successfully!")
        print(f"  The signature is authentic and matches the challenge")
    else:
        print(f"✗ Signature verification failed!")
        return
    
    # 6. Test with Modified Data
    print("\n6. Testing with Modified Data (Should Fail)...")
    print("-" * 80)
    modified_challenge = challenge[:-1] + b'\x00'
    is_valid_modified = verify_signature(modified_challenge, signature, public_key)
    
    if not is_valid_modified:
        print(f"✓ Correctly detected tampered data!")
        print(f"  Signature verification failed as expected")
    else:
        print(f"✗ WARNING: Signature verified for tampered data!")
    
    # Summary
    print("\n" + "=" * 80)
    print("Certificate-Based Digital Signing Test Complete!")
    print("=" * 80)
    print("\nSummary:")
    print("  ✓ Certificate loaded and parsed from PEM format")
    print("  ✓ Private key loaded from PEM format")
    print("  ✓ Random 256-bit challenge generated")
    print("  ✓ Challenge digitally signed with RSA-PSS-SHA256")
    print("  ✓ Signature verified successfully using certificate's public key")
    print("  ✓ Tampered data correctly rejected")
    print("\nThe sensor can now use certificate-based authentication!")
    print("\nCertificate Details:")
    print(f"  - Subject CN: {cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value}")
    print(f"  - Organization: {cert.subject.get_attributes_for_oid(x509.NameOID.ORGANIZATION_NAME)[0].value}")
    print(f"  - Valid for: {(cert.not_valid_after - cert.not_valid_before).days} days")


if __name__ == "__main__":
    main()

# Made with Bob