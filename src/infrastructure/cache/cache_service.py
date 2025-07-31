"""
Cache Service Implementation - Infrastructure Layer
Implements CacheService interface with multiple backend options
"""

import os
import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path
from ...core import CacheService

logger = logging.getLogger(__name__)


class FileCacheService(CacheService):
    """
    File-based cache implementation
    
    Principle: Strategy Pattern for cache backends
    - Can be easily swapped with Redis, SQLite, etc.
    - Implements interface segregation
    """
    
    def __init__(self, cache_dir: Optional[str] = None, default_ttl: int = 604800):
        """
        Initialize file cache service
        
        Args:
            cache_dir: Directory for cache files
            default_ttl: Default TTL in seconds (default: 7 days)
        """
        self.cache_dir = Path(cache_dir) if cache_dir else Path.home() / ".voicesub_cache"
        self.default_ttl = default_ttl
        
        # Create cache directory
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Metadata file for TTL tracking
        self.metadata_file = self.cache_dir / "_metadata.json"
        self._load_metadata()
        
        logger.info(f"File cache initialized at: {self.cache_dir}")
    
    def get(self, key: str) -> Optional[str]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        if not self._is_valid_key(key):
            return None
        
        # Check if key is expired
        if self._is_expired(key):
            self._remove_expired_key(key)
            return None
        
        cache_file = self._get_cache_file_path(key)
        
        try:
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('value')
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to read cache file {cache_file}: {e}")
            # Remove corrupted cache file
            cache_file.unlink(missing_ok=True)
        
        return None
    
    def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (None for default)
        """
        if not self._is_valid_key(key) or not value:
            return
        
        ttl = ttl or self.default_ttl
        expiry_time = datetime.now() + timedelta(seconds=ttl)
        
        cache_file = self._get_cache_file_path(key)
        
        try:
            # Ensure directory exists
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write cache data
            data = {
                'value': value,
                'created_at': datetime.now().isoformat(),
                'expires_at': expiry_time.isoformat()
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Update metadata
            self._update_metadata(key, expiry_time)
            
            logger.debug(f"Cached value for key: {key[:20]}...")
            
        except (IOError, OSError) as e:
            logger.error(f"Failed to write cache file {cache_file}: {e}")
    
    def generate_key(self, **kwargs) -> str:
        """
        Generate cache key from parameters
        
        Args:
            **kwargs: Key-value pairs to include in key
            
        Returns:
            Generated cache key
        """
        # Sort kwargs for consistent key generation
        sorted_items = sorted(kwargs.items())
        key_string = '|'.join(f"{k}:{v}" for k, v in sorted_items)
        
        # Create hash for manageable key length
        key_hash = hashlib.sha256(key_string.encode()).hexdigest()
        
        # Include some readable info for debugging
        readable_part = '_'.join(str(v)[:10] for k, v in sorted_items[:3])
        readable_part = ''.join(c for c in readable_part if c.isalnum() or c in '_-')
        
        return f"{readable_part}_{key_hash[:16]}"
    
    def clear_expired(self) -> int:
        """
        Clear all expired cache entries
        
        Returns:
            Number of entries cleared
        """
        cleared_count = 0
        current_time = datetime.now()
        
        # Get all expired keys from metadata
        expired_keys = []
        for key, expiry_str in self.metadata.get('expiry_times', {}).items():
            try:
                expiry_time = datetime.fromisoformat(expiry_str)
                if current_time > expiry_time:
                    expired_keys.append(key)
            except ValueError:
                # Invalid expiry time, consider expired
                expired_keys.append(key)
        
        # Remove expired files
        for key in expired_keys:
            cache_file = self._get_cache_file_path(key)
            if cache_file.exists():
                cache_file.unlink()
                cleared_count += 1
            
            # Remove from metadata
            self.metadata.get('expiry_times', {}).pop(key, None)
        
        # Save updated metadata
        if expired_keys:
            self._save_metadata()
            logger.info(f"Cleared {cleared_count} expired cache entries")
        
        return cleared_count
    
    def clear_all(self) -> None:
        """Clear all cache entries"""
        import shutil
        
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            
        self.metadata = {'expiry_times': {}}
        self._save_metadata()
        
        logger.info("Cleared all cache entries")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache stats
        """
        total_files = 0
        total_size = 0
        expired_count = 0
        current_time = datetime.now()
        
        if self.cache_dir.exists():
            for cache_file in self.cache_dir.rglob("*.json"):
                if cache_file.name == "_metadata.json":
                    continue
                    
                total_files += 1
                total_size += cache_file.stat().st_size
        
        # Count expired entries
        for expiry_str in self.metadata.get('expiry_times', {}).values():
            try:
                expiry_time = datetime.fromisoformat(expiry_str)
                if current_time > expiry_time:
                    expired_count += 1
            except ValueError:
                expired_count += 1
        
        return {
            'total_entries': total_files,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / 1024 / 1024, 2),
            'expired_entries': expired_count,
            'cache_directory': str(self.cache_dir)
        }
    
    def _get_cache_file_path(self, key: str) -> Path:
        """Get cache file path for key"""
        # Use first 2 chars for subdirectory to avoid too many files in one dir
        subdir = key[:2] if len(key) >= 2 else "misc"
        return self.cache_dir / subdir / f"{key}.json"
    
    def _is_valid_key(self, key: str) -> bool:
        """Check if key is valid"""
        return bool(key and isinstance(key, str) and len(key) > 0)
    
    def _is_expired(self, key: str) -> bool:
        """Check if cache key is expired"""
        expiry_str = self.metadata.get('expiry_times', {}).get(key)
        if not expiry_str:
            return True
        
        try:
            expiry_time = datetime.fromisoformat(expiry_str)
            return datetime.now() > expiry_time
        except ValueError:
            return True
    
    def _remove_expired_key(self, key: str) -> None:
        """Remove expired key and its file"""
        cache_file = self._get_cache_file_path(key)
        cache_file.unlink(missing_ok=True)
        
        self.metadata.get('expiry_times', {}).pop(key, None)
        self._save_metadata()
    
    def _load_metadata(self) -> None:
        """Load metadata from file"""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
            else:
                self.metadata = {'expiry_times': {}}
        except (json.JSONDecodeError, IOError):
            logger.warning("Failed to load cache metadata, starting fresh")
            self.metadata = {'expiry_times': {}}
    
    def _save_metadata(self) -> None:
        """Save metadata to file"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2)
        except (IOError, OSError) as e:
            logger.error(f"Failed to save cache metadata: {e}")
    
    def _update_metadata(self, key: str, expiry_time: datetime) -> None:
        """Update metadata for a key"""
        if 'expiry_times' not in self.metadata:
            self.metadata['expiry_times'] = {}
        
        self.metadata['expiry_times'][key] = expiry_time.isoformat()
        self._save_metadata()


class MemoryCacheService(CacheService):
    """
    In-memory cache implementation for testing or simple use cases
    
    Principle: Strategy Pattern alternative implementation
    """
    
    def __init__(self, default_ttl: int = 3600):
        """
        Initialize memory cache
        
        Args:
            default_ttl: Default TTL in seconds (default: 1 hour)
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
        logger.info("Memory cache initialized")
    
    def get(self, key: str) -> Optional[str]:
        """Get value from memory cache"""
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        # Check expiry
        if datetime.now() > entry['expires_at']:
            del self.cache[key]
            return None
        
        return entry['value']
    
    def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """Set value in memory cache"""
        if not key or not value:
            return
        
        ttl = ttl or self.default_ttl
        expiry_time = datetime.now() + timedelta(seconds=ttl)
        
        self.cache[key] = {
            'value': value,
            'expires_at': expiry_time
        }
    
    def generate_key(self, **kwargs) -> str:
        """Generate cache key"""
        sorted_items = sorted(kwargs.items())
        key_string = '|'.join(f"{k}:{v}" for k, v in sorted_items)
        return hashlib.sha256(key_string.encode()).hexdigest()[:32]
    
    def clear_expired(self) -> int:
        """Clear expired entries"""
        current_time = datetime.now()
        expired_keys = [
            key for key, entry in self.cache.items()
            if current_time > entry['expires_at']
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        return len(expired_keys)
    
    def clear_all(self) -> None:
        """Clear all entries"""
        self.cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_entries = len(self.cache)
        expired_count = self.clear_expired()  # This also cleans up
        
        return {
            'total_entries': total_entries,
            'expired_entries': expired_count,
            'cache_type': 'memory'
        }
