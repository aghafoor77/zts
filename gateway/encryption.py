"""
Encryption utilities for the Gateway
"""
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes


class AESEncryption:
    """AES encryption/decryption handler"""
    
    def __init__(self, key: str):
        """
        Initialize AES encryption with a key
        
        Args:
            key: Encryption key (will be padded/truncated to 16 bytes for AES-128)
        """
        # Ensure key is exactly 16 bytes for AES-128
        self.key = key.encode('utf-8')[:16].ljust(16, b'\0')
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext using AES-CBC
        
        Args:
            plaintext: Text to encrypt
            
        Returns:
            str: Base64 encoded encrypted data (IV + ciphertext)
        """
        # Generate random IV
        iv = get_random_bytes(16)
        
        # Create cipher
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        
        # Pad and encrypt
        padded_data = pad(plaintext.encode('utf-8'), AES.block_size)
        ciphertext = cipher.encrypt(padded_data)
        
        # Combine IV and ciphertext, then base64 encode
        encrypted_data = iv + ciphertext
        return base64.b64encode(encrypted_data).decode('utf-8')
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt AES-CBC encrypted data
        
        Args:
            encrypted_data: Base64 encoded encrypted data (IV + ciphertext)
            
        Returns:
            str: Decrypted plaintext
        """
        # Decode base64
        encrypted_bytes = base64.b64decode(encrypted_data)
        
        # Extract IV and ciphertext
        iv = encrypted_bytes[:16]
        ciphertext = encrypted_bytes[16:]
        
        # Create cipher and decrypt
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        padded_plaintext = cipher.decrypt(ciphertext)
        
        # Unpad and decode
        plaintext = unpad(padded_plaintext, AES.block_size)
        return plaintext.decode('utf-8')

# Made with # Com 
