"""
Radioplayer API Authentication
Implements RSA-SHA256 signature-based authentication for Radioplayer Partner API (WRAPI)
"""

import base64
import hashlib
import os
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
import logging

logger = logging.getLogger(__name__)


class RadioplayerAuth:
    """
    Radioplayer API Authentication Handler
    
    Implements signature-based authentication using:
    - API Key (keyId)
    - RSA Private Key
    - SHA256 hashing
    """
    
    def __init__(self):
        """Initialize Radioplayer authentication"""
        # Load credentials from environment
        self.api_key = os.getenv('RADIOPLAYER_API_KEY', '')
        self.private_key_path = os.getenv('RADIOPLAYER_PRIVATE_KEY_PATH', '')
        
        # Try to load private key from file or environment variable
        self.private_key = None
        if self.private_key_path and Path(self.private_key_path).exists():
            self.private_key = self._load_private_key_from_file(self.private_key_path)
        else:
            # Try loading from environment variable directly (PEM string)
            pem_string = os.getenv('RADIOPLAYER_PRIVATE_KEY_PEM', '')
            if pem_string:
                self.private_key = self._load_private_key_from_string(pem_string)
        
        self.is_configured = bool(self.api_key and self.private_key)
        
        if self.is_configured:
            logger.info("Radioplayer authentication configured successfully")
        else:
            logger.warning("Radioplayer authentication not configured - missing credentials")
    
    def _load_private_key_from_file(self, key_path: str):
        """Load RSA private key from PEM file"""
        try:
            with open(key_path, 'rb') as key_file:
                private_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=None,
                    backend=default_backend()
                )
            return private_key
        except Exception as e:
            logger.error(f"Failed to load private key from file: {e}")
            return None
    
    def _load_private_key_from_string(self, pem_string: str):
        """Load RSA private key from PEM string"""
        try:
            private_key = serialization.load_pem_private_key(
                pem_string.encode('utf-8'),
                password=None,
                backend=default_backend()
            )
            return private_key
        except Exception as e:
            logger.error(f"Failed to load private key from string: {e}")
            return None
    
    def get_auth_headers(self, method: str = 'GET', path: str = '/') -> Dict[str, str]:
        """
        Generate authentication headers for Radioplayer API request
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: API endpoint path
        
        Returns:
            Dictionary with authentication headers
        """
        if not self.is_configured:
            logger.warning("Radioplayer authentication not configured")
            return {}
        
        # Generate date in RFC 2822 format
        date_str = self._get_rfc2822_date()
        
        # Create signature string
        # Format: (request-target): get /path\ndate: Wed, 03 Dec 2025 21:39:00 GMT
        signature_string = f"(request-target): {method.lower()} {path}\ndate: {date_str}"
        
        # Sign the string
        signature = self._sign_string(signature_string)
        
        if not signature:
            logger.error("Failed to generate signature")
            return {}
        
        # Create Authorization header
        # Format: Signature keyId="your-key",algorithm="rsa-sha256",signature="base64-signature"
        auth_header = (
            f'Signature keyId="{self.api_key}",'
            f'algorithm="rsa-sha256",'
            f'headers="(request-target) date",'
            f'signature="{signature}"'
        )
        
        return {
            'Date': date_str,
            'Authorization': auth_header,
            'User-Agent': 'DragonKarauAI/1.0',
            'Accept': 'application/json'
        }
    
    def _get_rfc2822_date(self) -> str:
        """
        Get current date in RFC 2822 format
        Example: Wed, 03 Dec 2025 21:39:00 GMT
        """
        return datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    def _sign_string(self, data: str) -> Optional[str]:
        """
        Sign a string using RSA-SHA256
        
        Args:
            data: String to sign
        
        Returns:
            Base64-encoded signature
        """
        if not self.private_key:
            return None
        
        try:
            # Sign the data using RSA-SHA256
            signature = self.private_key.sign(
                data.encode('utf-8'),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            
            # Encode signature as base64
            signature_b64 = base64.b64encode(signature).decode('utf-8')
            
            return signature_b64
        
        except Exception as e:
            logger.error(f"Failed to sign string: {e}")
            return None
    
    def test_authentication(self) -> Dict[str, any]:
        """
        Test authentication configuration
        
        Returns:
            Dictionary with test results
        """
        return {
            'configured': self.is_configured,
            'api_key_present': bool(self.api_key),
            'private_key_loaded': bool(self.private_key),
            'api_key_preview': f"{self.api_key[:8]}..." if self.api_key else None
        }


# Singleton instance
_radioplayer_auth = None


def get_radioplayer_auth() -> RadioplayerAuth:
    """Get singleton instance of RadioplayerAuth"""
    global _radioplayer_auth
    if _radioplayer_auth is None:
        _radioplayer_auth = RadioplayerAuth()
    return _radioplayer_auth
