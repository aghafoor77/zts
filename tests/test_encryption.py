"""
Unit tests for encryption module
"""
import unittest
from gateway.encryption import AESEncryption


class TestAESEncryption(unittest.TestCase):
    """Test cases for AES encryption"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.key = "TestSecretKey123"
        self.encryption = AESEncryption(self.key)
    
    def test_encrypt_decrypt(self):
        """Test encryption and decryption"""
        plaintext = "Hello, World!"
        
        # Encrypt
        encrypted = self.encryption.encrypt(plaintext)
        self.assertIsInstance(encrypted, str)
        self.assertNotEqual(encrypted, plaintext)
        
        # Decrypt
        decrypted = self.encryption.decrypt(encrypted)
        self.assertEqual(decrypted, plaintext)
    
    def test_encrypt_json(self):
        """Test encryption of JSON data"""
        import json
        data = {"temperature": 25.5, "humidity": 60.0}
        plaintext = json.dumps(data)
        
        # Encrypt
        encrypted = self.encryption.encrypt(plaintext)
        
        # Decrypt
        decrypted = self.encryption.decrypt(encrypted)
        decrypted_data = json.loads(decrypted)
        
        self.assertEqual(decrypted_data, data)
    
    def test_different_keys(self):
        """Test that different keys produce different results"""
        plaintext = "Test message"
        
        encryption1 = AESEncryption("Key1")
        encryption2 = AESEncryption("Key2")
        
        encrypted1 = encryption1.encrypt(plaintext)
        encrypted2 = encryption2.encrypt(plaintext)
        
        # Different keys should produce different ciphertexts
        self.assertNotEqual(encrypted1, encrypted2)
        
        # Decryption with wrong key should fail
        with self.assertRaises(Exception):
            encryption1.decrypt(encrypted2)


if __name__ == '__main__':
    unittest.main()

# Made with Bob
