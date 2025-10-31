"""
IPFS storage service for NileFi using Pinata.
Handles document uploads and retrieval via IPFS.
"""

import os
import requests
import magic
from typing import Dict, Optional, BinaryIO
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile


class IPFSStorageService:
    """
    IPFS storage service using Pinata API.
    Provides document upload, pinning, and retrieval functionality.
    """
    
    def __init__(self):
        self.api_key = settings.PINATA_API_KEY
        self.secret_key = settings.PINATA_SECRET_KEY
        self.jwt_token = settings.PINATA_JWT
        self.gateway_url = settings.IPFS_GATEWAY
        
        self.base_url = "https://api.pinata.cloud"
        self.pin_url = f"{self.base_url}/pinning/pinFileToIPFS"
        self.unpin_url = f"{self.base_url}/pinning/unpin"
        
        # Setup headers
        if self.jwt_token:
            self.headers = {
                "Authorization": f"Bearer {self.jwt_token}"
            }
        else:
            self.headers = {
                "pinata_api_key": self.api_key,
                "pinata_secret_api_key": self.secret_key
            }
    
    def upload_file(
        self,
        file: UploadedFile,
        filename: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Upload a file to IPFS via Pinata.
        
        Args:
            file: Django UploadedFile object
            filename: Optional custom filename
            metadata: Optional metadata dict
        
        Returns:
            Dict with CID and upload info, or None if failed
        """
        
        # Validate file
        if not self._validate_file(file):
            print(f"File validation failed: {file.name}")
            return None
        
        try:
            # Prepare file
            file_name = filename or file.name
            files = {
                'file': (file_name, file.read(), file.content_type)
            }
            
            # Prepare metadata
            pin_metadata = {
                "name": file_name,
                "keyvalues": metadata or {}
            }
            
            data = {
                "pinataMetadata": str(pin_metadata),
                "pinataOptions": str({"cidVersion": 1})
            }
            
            # Upload to Pinata
            if not self.api_key:
                # Mock mode for development without Pinata credentials
                return self._mock_upload(file_name)
            
            response = requests.post(
                self.pin_url,
                files=files,
                data=data,
                headers=self.headers,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "cid": result["IpfsHash"],
                    "size": result["PinSize"],
                    "timestamp": result["Timestamp"],
                    "filename": file_name,
                    "url": f"{self.gateway_url}{result['IpfsHash']}"
                }
            else:
                print(f"Pinata upload failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error uploading to IPFS: {e}")
            return None
    
    def get_file_url(self, cid: str) -> str:
        """
        Get gateway URL for accessing a file by CID.
        
        Args:
            cid: IPFS Content Identifier
        
        Returns:
            Full gateway URL
        """
        return f"{self.gateway_url}{cid}"
    
    def unpin_file(self, cid: str) -> bool:
        """
        Unpin a file from Pinata (remove from storage).
        Use with caution - only for truly unused files.
        
        Args:
            cid: IPFS Content Identifier to unpin
        
        Returns:
            True if successful
        """
        if not self.api_key:
            return True  # Mock mode
        
        try:
            url = f"{self.unpin_url}/{cid}"
            response = requests.delete(url, headers=self.headers, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Error unpinning file {cid}: {e}")
            return False
    
    def _validate_file(self, file: UploadedFile) -> bool:
        """
        Validate uploaded file.
        Checks size and file type.
        """
        # Check size
        max_size = settings.MAX_UPLOAD_SIZE
        if file.size > max_size:
            print(f"File too large: {file.size} bytes (max: {max_size})")
            return False
        
        # Check file type
        allowed_types = settings.ALLOWED_FILE_TYPES
        file_ext = file.name.split('.')[-1].lower() if '.' in file.name else ''
        
        if file_ext not in allowed_types:
            print(f"File type not allowed: {file_ext}")
            return False
        
        # Additional MIME type check using python-magic
        try:
            file.seek(0)
            file_content = file.read(2048)  # Read first 2KB
            file.seek(0)  # Reset
            
            mime = magic.from_buffer(file_content, mime=True)
            
            # Define acceptable MIME types
            acceptable_mimes = [
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'application/vnd.ms-excel',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            ]
            
            if mime not in acceptable_mimes:
                print(f"MIME type not allowed: {mime}")
                return False
                
        except Exception as e:
            print(f"MIME type check failed: {e}")
            # Continue anyway in development
        
        return True
    
    def _mock_upload(self, filename: str) -> Dict:
        """Generate mock upload result for development"""
        import hashlib
        import time
        
        # Generate fake CID
        mock_cid = hashlib.sha256(f"{filename}{time.time()}".encode()).hexdigest()[:46]
        
        return {
            "cid": f"Qm{mock_cid}",
            "size": 1024,
            "timestamp": time.time(),
            "filename": filename,
            "url": f"{self.gateway_url}Qm{mock_cid}"
        }


# Singleton instance
ipfs_storage_service = IPFSStorageService()
