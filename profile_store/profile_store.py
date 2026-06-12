"""
Profile Store - Black Box Component
Generates device profiles based on device information and certificates
"""
import json
import hashlib
from typing import Dict, Any
from config.config import (
    DeviceType, MessageType, Protocol, BinaryFlag,
    EncryptionType, AuthenticationType, RecommendedProtocol
)


class ProfileStore:
    """
    Mock Profile Store that generates device profiles based on device information.
    This is treated as a black box component.
    """
    
    def __init__(self):
        """Initialize the Profile Store"""
        self.profiles = {}
    
    def verify_certificate(self, certificate: str) -> bool:
        """
        Verify device certificate (mock implementation)
        
        Args:
            certificate: Device certificate string
            
        Returns:
            bool: True if certificate is valid
        """
        # Mock verification - in real implementation, this would verify against CA
        return certificate and len(certificate) > 10
    
    def generate_profile(self, device_info: Dict[str, Any], certificate: str) -> Dict[str, Any]:
        """
        Generate a device profile based on device information and certificate
        
        Args:
            device_info: Dictionary containing device_type, manufacturer, model
            certificate: Device certificate
            
        Returns:
            Dict containing the generated profile
        """
        if not self.verify_certificate(certificate):
            raise ValueError("Invalid device certificate")
        
        device_type = device_info.get('device_type', DeviceType.SENSOR)
        manufacturer = device_info.get('manufacturer', 'Unknown')
        model = device_info.get('model', 'Unknown')
        
        # Generate a unique profile ID based on device info
        profile_id = self._generate_profile_id(device_type, manufacturer, model)
        
        # Determine authentication type based on certificate
        # If certificate is in PEM format (contains BEGIN CERTIFICATE), use CERT_BASED
        # Otherwise, use USERNAME_PASSWORD
        auth_type = self._determine_auth_type(certificate)
        
        # Generate profile based on device characteristics
        profile = {
            "profileID": profile_id,
            "device_type": device_type,
            "manufacturer": manufacturer,
            "model": model,
            "message_type": MessageType.TELEMETRY,
            "protocol": Protocol.MQTT,
            "firmware_version": 1.0,
            "supports_encryption": BinaryFlag.YES,
            "supports_authentication": BinaryFlag.YES,
            "secure_boot": BinaryFlag.YES,
            "update_frequency_days": 30,
            "required_encryption": EncryptionType.AES,
            "required_authentication": auth_type,
            "required_key_rotation_days": 90,
            "recommended_protocol": RecommendedProtocol.MQTT,
            "risk_score": self._calculate_risk_score(device_info),
            "certificate_hash": self._hash_certificate(certificate) if auth_type == AuthenticationType.CERT_BASED else None
        }
        
        # Store the profile
        self.profiles[profile_id] = profile
        print(json.dumps(profile, indent=4))
        
        return profile
    
    def _generate_profile_id(self, device_type: str, manufacturer: str, model: str) -> str:
        """
        Generate a unique profile ID
        
        Args:
            device_type: Type of device
            manufacturer: Device manufacturer
            model: Device model
            
        Returns:
            str: Unique profile ID
        """
        data = f"{device_type}:{manufacturer}:{model}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _calculate_risk_score(self, device_info: Dict[str, Any]) -> float:
        """
        Calculate risk score based on device characteristics
        
        Args:
            device_info: Device information
            
        Returns:
            float: Risk score between 0 and 1
        """
        # Mock risk calculation - in real implementation, this would be more sophisticated
        base_score = 0.3
        
        # Adjust based on device type
        device_type = device_info.get('device_type', DeviceType.SENSOR)
        if device_type == DeviceType.CAMERA:
            base_score += 0.2
        elif device_type == DeviceType.ACTUATOR:
            base_score += 0.3
        
    
    def _determine_auth_type(self, certificate: str) -> int:
        """
        Determine authentication type based on certificate format
        
        Args:
            certificate: Device certificate string
            
        Returns:
            int: Authentication type (USERNAME_PASSWORD or CERT_BASED)
        """
        # Check if certificate is in PEM format
        if "-----BEGIN CERTIFICATE-----" in certificate and "-----END CERTIFICATE-----" in certificate:
            return AuthenticationType.CERT_BASED
        else:
            return AuthenticationType.USERNAME_PASSWORD
    
    def _hash_certificate(self, certificate: str) -> str:
        """
        Generate hash of certificate for verification
        
        Args:
            certificate: Device certificate in PEM format
            
        Returns:
            str: SHA-256 hash of certificate
        """
        return hashlib.sha256(certificate.encode()).hexdigest()
        return min(base_score, 1.0)
    
    def get_profile(self, profile_id: str) -> Dict[str, Any]:
        """
        Retrieve a stored profile
        
        Args:
            profile_id: Profile ID
            
        Returns:
            Dict: Profile data
        """
        return self.profiles.get(profile_id)

# Made with # Com 
