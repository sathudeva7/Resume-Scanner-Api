import os
import uuid
import hashlib
from pathlib import Path
from typing import List, Tuple, Optional
from fastapi import UploadFile, HTTPException
from app.core.config import settings

# Try to import python-magic, but make it optional
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    print("Warning: python-magic not available. File type detection will use extension-based fallback.")


class FileHandler:
    """Utility class for handling file uploads and validation"""
    
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(exist_ok=True)
        self.allowed_extensions = set(settings.ALLOWED_FILE_EXTENSIONS)
        self.max_file_size = settings.MAX_FILE_SIZE
        self._spaces_client = None
    
    def validate_file(self, file: UploadFile) -> Tuple[bool, List[str]]:
        """
        Validate uploaded file
        Returns: (is_valid, list_of_issues)
        """
        issues = []
        
        # Check filename
        if not file.filename:
            issues.append("Filename is required")
            return False, issues
        
        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in self.allowed_extensions:
            issues.append(f"File extension {file_ext} not allowed. Allowed: {', '.join(self.allowed_extensions)}")
        
        # Check file size (if available)
        if hasattr(file, 'size') and file.size:
            if file.size > self.max_file_size:
                issues.append(f"File size {file.size} exceeds maximum allowed size {self.max_file_size}")
        
        return len(issues) == 0, issues
    
    def detect_file_type(self, file_path: Path) -> str:
        """Detect file type using python-magic or fallback to extension-based detection"""
        # Extension-based MIME type mapping
        ext = file_path.suffix.lower()
        mime_map = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword',
            '.txt': 'text/plain'
        }
        
        # Try python-magic if available
        if MAGIC_AVAILABLE:
            try:
                mime_type = magic.from_file(str(file_path), mime=True)
                return mime_type
            except Exception:
                # Fallback to extension-based detection if magic fails
                pass
        
        # Extension-based detection (fallback)
        return mime_map.get(ext, 'application/octet-stream')
    
    def generate_file_id(self, filename: str) -> str:
        """Generate unique file ID"""
        return str(uuid.uuid4())
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    # -------- DigitalOcean Spaces (S3) helpers --------
    def _get_spaces_client(self):
        """Initialize and cache a boto3 client for Spaces if enabled"""
        if not settings.USE_SPACES:
            return None
        if self._spaces_client is not None:
            return self._spaces_client
        try:
            import boto3
        except ImportError as e:
            raise HTTPException(status_code=500, detail="boto3 is required for Spaces but not installed")
        if not all([
            settings.SPACES_ENDPOINT_URL,
            settings.SPACES_REGION,
            settings.SPACES_ACCESS_KEY_ID,
            settings.SPACES_SECRET_ACCESS_KEY,
            settings.SPACES_BUCKET_NAME
        ]):
            raise HTTPException(status_code=500, detail="Spaces is enabled but configuration is incomplete")
        self._spaces_client = boto3.client(
            "s3",
            region_name='lon1',
            endpoint_url='https://resume-scanner.lon1.digitaloceanspaces.com',
            aws_access_key_id='DO00JTMEPKGRXPAFGXYT',
            aws_secret_access_key='j54Qklwe6zyOnFdvqPG9ToDaBOteWTMByyqeewYpbNo',
        )
        return self._spaces_client
    
    def _build_spaces_key(self, filename: str) -> str:
        """Build object key with optional prefix"""
        prefix = settings.SPACES_KEY_PREFIX.strip("/") if settings.SPACES_KEY_PREFIX else ""
        if prefix:
            return f"{prefix}/{filename}"
        return filename
    
    def _build_spaces_url(self, key: str) -> str:
        """Compute public URL for the object, using CDN base if provided"""
        if settings.SPACES_CDN_BASE_URL:
            base = settings.SPACES_CDN_BASE_URL.rstrip("/")
            return f"{base}/{key}"
        # default endpoint/bucket URL
        endpoint = settings.SPACES_ENDPOINT_URL.rstrip("/") if settings.SPACES_ENDPOINT_URL else ""
        return f"{endpoint}/{settings.SPACES_BUCKET_NAME}/{key}"
    
    async def save_uploaded_file(self, file: UploadFile, job_id: str) -> Tuple[Path, dict]:
        """
        Save uploaded file to disk
        Returns: (file_path, file_metadata)
        """
        # Validate file first
        is_valid, issues = self.validate_file(file)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"File validation failed: {', '.join(issues)}")
        
        # Generate safe filename
        file_ext = Path(file.filename).suffix.lower()
        safe_filename = f"{job_id}{file_ext}"
        file_path = self.upload_dir / safe_filename
        
        # Save file
        try:
            content = await file.read()
            
            # Check content size
            if len(content) > self.max_file_size:
                raise HTTPException(
                    status_code=413,
                    detail=f"File size {len(content)} exceeds maximum allowed size {self.max_file_size}"
                )
            
            with open(file_path, "wb") as f:
                f.write(content)
            
            # Generate metadata
            file_metadata = {
                "original_filename": file.filename,
                "saved_filename": safe_filename,
                "file_path": str(file_path),
                "file_size": len(content),
                "file_hash": self.calculate_file_hash(file_path),
                "mime_type": self.detect_file_type(file_path),
                "job_id": job_id
            }
            
            # Optionally upload to DigitalOcean Spaces
            if settings.USE_SPACES:
                client = self._get_spaces_client()
                object_key = self._build_spaces_key(safe_filename)
                extra_args = {"ACL": settings.SPACES_ACL}
                mime_type = file_metadata["mime_type"] or "application/octet-stream"
                if mime_type:
                    extra_args["ContentType"] = mime_type
                try:
                    client.upload_file(
                        Filename=str(file_path),
                        Bucket=settings.SPACES_BUCKET_NAME,
                        Key=object_key,
                        ExtraArgs=extra_args
                    )
                except Exception as e:
                    # If upload fails, keep local file and bubble up error
                    raise HTTPException(status_code=500, detail=f"Upload to Spaces failed: {str(e)}")
                # Add Spaces metadata
                file_metadata.update({
                    "spaces_bucket": settings.SPACES_BUCKET_NAME,
                    "spaces_key": object_key,
                    "spaces_url": self._build_spaces_url(object_key)
                })
                # Optionally delete local copy (NOT recommended if downstream expects local path)
                if settings.SPACES_DELETE_LOCAL_AFTER_UPLOAD:
                    try:
                        if file_path.exists():
                            file_path.unlink()
                            file_metadata["file_path"] = None
                    except Exception:
                        pass
            
            return file_path, file_metadata
            
        except Exception as e:
            # Clean up file if it was created
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    def delete_file(self, file_path: Path) -> bool:
        """Delete file from disk"""
        try:
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception:
            return False
    
    def delete_spaces_object(self, saved_filename: str) -> bool:
        """Delete uploaded object from DigitalOcean Spaces. Returns True if deleted or not found."""
        if not settings.USE_SPACES:
            return False
        try:
            client = self._get_spaces_client()
            key = self._build_spaces_key(saved_filename)
            client.delete_object(Bucket=settings.SPACES_BUCKET_NAME, Key=key)
            return True
        except Exception:
            return False
    
    def get_file_info(self, file_path: Path) -> Optional[dict]:
        """Get file information"""
        if not file_path.exists():
            return None
        
        try:
            stat = file_path.stat()
            return {
                "file_path": str(file_path),
                "file_size": stat.st_size,
                "created_at": stat.st_ctime,
                "modified_at": stat.st_mtime,
                "mime_type": self.detect_file_type(file_path),
                "file_hash": self.calculate_file_hash(file_path)
            }
        except Exception:
            return None
    
    def cleanup_old_files(self, max_age_days: int = 7) -> int:
        """Clean up old uploaded files"""
        import time
        
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 60 * 60
        deleted_count = 0
        
        try:
            for file_path in self.upload_dir.iterdir():
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        file_path.unlink()
                        deleted_count += 1
        except Exception:
            pass
        
        return deleted_count


# Global file handler instance
file_handler = FileHandler()


def get_file_handler() -> FileHandler:
    """Get file handler instance"""
    return file_handler


def validate_file_extension(filename: str) -> bool:
    """Quick validation of file extension"""
    if not filename:
        return False
    ext = Path(filename).suffix.lower()
    return ext in settings.ALLOWED_FILE_EXTENSIONS


def get_safe_filename(filename: str, job_id: str) -> str:
    """Generate safe filename for storage"""
    ext = Path(filename).suffix.lower()
    return f"{job_id}{ext}"
