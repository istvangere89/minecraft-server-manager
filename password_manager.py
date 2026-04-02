"""
Password manager module for hashing and verifying passwords.
Uses SHA256 for secure password storage.
"""

import hashlib


def hash_password(password: str) -> str:
    """
    Hash a password using SHA256.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        Hexadecimal string representation of the hash
    """
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a password against a stored hash.
    
    Args:
        password: Plain text password to verify
        password_hash: Stored hash to compare against
        
    Returns:
        True if password matches the hash, False otherwise
    """
    return hash_password(password) == password_hash
