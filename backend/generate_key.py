#!/usr/bin/env python3
"""
Generate encryption key for LLM Chat Platform
"""

from cryptography.fernet import Fernet

def generate_key():
    """Generate a new Fernet encryption key"""
    key = Fernet.generate_key()
    return key.decode()

if __name__ == "__main__":
    key = generate_key()
    print("Generated Encryption Key:")
    print(key)
    print("\nAdd this to your .env file:")
    print(f"ENCRYPTION_KEY={key}")
