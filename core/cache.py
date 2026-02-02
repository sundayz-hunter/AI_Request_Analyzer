# -*- coding: utf-8 -*-

import json
import os
import time
from core.config_loader import ConfigLoader

class AnalysisCache:
    """
    Manages caching of analysis results to improve performance
    and reduce API calls for repeated analyses.
    """

    def __init__(self, callbacks):
        """
        Initialize the cache system.
        
        Args:
            callbacks: Burp's callbacks object for accessing extension functionality
        """
        self._callbacks = callbacks
        self._analyzeCache = {}
        self._cachePath = None
        self._stdout = callbacks.getStdout()
        # Store a reference to the extender to access the UI
        self._extender = None  # Will be defined later via set_extender
        
        # Load configuration
        self._config = ConfigLoader(callbacks)
        
        # Cache metadata to track entry age
        self._cacheMetadata = {}

        # Cache statistics - simplifié pour ne garder que les valeurs essentielles
        self._cacheStats = {
            "size": 0,      # Size in bytes
            "entries": 0    # Number of entries
        }

        # Setup cache file path
        try:
            extensionsDir = callbacks.getExtensionFilename()
            if extensionsDir:
                parentDir = os.path.dirname(extensionsDir)
                self._cachePath = os.path.join(parentDir, "ai_analyzer_cache.json")

                # Load cache if it exists
                if os.path.exists(self._cachePath):
                    try:
                        with open(self._cachePath, 'r') as f:
                            cacheData = json.load(f)
                            self._analyzeCache = cacheData.get("cache", {})
                            self._cacheMetadata = cacheData.get("metadata", {})

                            # Add timestamps for entries without metadata (backward compatibility)
                            for key in self._analyzeCache:
                                if key not in self._cacheMetadata:
                                    self._cacheMetadata[key] = {
                                        "timestamp": time.time(),
                                        "size": len(self._analyzeCache[key])
                                    }

                            # Recalculate statistics
                            self._cacheStats["entries"] = len(self._analyzeCache)
                            self._cacheStats["size"] = sum(meta.get("size", 0) for meta in self._cacheMetadata.values())

                            # Clean up cache based on age and size limits
                            self._clean_cache()
                    except Exception as e:
                        self._stdout.write("Error loading cache: " + str(e) + "\n")
        except Exception as e:
            self._stdout.write("Error setting up cache file: " + str(e) + "\n")
    
    def _clean_cache(self):
        """
        Clean the cache by removing expired entries and enforcing size limits.
        This method also makes sure the total cache size doesn't exceed the maximum allowed.
        """
        try:
            # Get current time and configuration values
            current_time = time.time()
            max_age_days = self._config.get("CACHE_MAX_AGE_DAYS", 30)
            max_age_seconds = max_age_days * 24 * 60 * 60
            max_size_bytes = self._config.get("CACHE_MAX_SIZE_MB", 100) * 1024 * 1024
            max_entries = self._config.get("CACHE_MAX_ENTRIES", 1000)
            
            # Track if changes were made
            changes_made = False
            
            # Remove expired entries
            for key, metadata in list(self._cacheMetadata.items()):
                if current_time - metadata.get("timestamp", 0) > max_age_seconds:
                    if key in self._analyzeCache:
                        # Update size statistic
                        self._cacheStats["size"] -= self._cacheMetadata[key].get("size", 0)
                        
                        # Remove entry
                        del self._analyzeCache[key]
                        del self._cacheMetadata[key]
                        changes_made = True
            
            # Check if we need to prune by size or entry count
            if (self._cacheStats["size"] > max_size_bytes) or (len(self._analyzeCache) > max_entries):
                # Sort entries by timestamp (oldest first)
                sorted_entries = sorted(
                    [(k, meta.get("timestamp", 0)) for k, meta in self._cacheMetadata.items()],
                    key=lambda x: x[1]
                )
                
                # Prune entries until we're under the limits
                for key, _ in sorted_entries:
                    if (self._cacheStats["size"] <= max_size_bytes) and (len(self._analyzeCache) <= max_entries):
                        break
                    
                    # Skip if entry was already removed (e.g., expired)
                    if key not in self._analyzeCache:
                        continue
                    
                    # Update size statistic
                    self._cacheStats["size"] -= self._cacheMetadata[key].get("size", 0)
                    
                    # Remove entry
                    del self._analyzeCache[key]
                    del self._cacheMetadata[key]
                    changes_made = True
            
            # Update number of entries if changes have been made
            if changes_made:
                self._cacheStats["entries"] = len(self._analyzeCache)
                # Save changes to file
                self._save_cache_to_file()
                
        except Exception as e:
            self._stdout.write("Error cleaning cache: " + str(e) + "\n")

    def get_cached_analysis(self, message_hash, is_request):
        """
        Retrieve cached analysis result if available.
        
        Args:
            message_hash: Hash of the message
            is_request: Whether the message is a request or response
            
        Returns:
            Cached analysis result or None if not found
        """
        key = "{0}_{1}".format(message_hash, "req" if is_request else "resp")
        result = self._analyzeCache.get(key)

        # Update last access timestamp if result found
        if result and key in self._cacheMetadata:
            self._cacheMetadata[key]["last_access"] = time.time()

        return result

    def set_extender(self, extender):
        """
        Set a reference to the extender for UI updates.
        
        Args:
            extender: The main extender object
        """
        self._extender = extender
        
    def set_cached_analysis(self, message_hash, is_request, result):
        """
        Store analysis result in cache.
        
        Args:
            message_hash: Hash of the message
            is_request: Whether the message is a request or response
            result: Analysis result to cache
        """
        key = "{0}_{1}".format(message_hash, "req" if is_request else "resp")
        result_size = len(result)

        # Subtract size of existing entry if present
        if key in self._analyzeCache:
            old_size = self._cacheMetadata.get(key, {}).get("size", 0)
            self._cacheStats["size"] -= old_size

        # Add new entry
        self._analyzeCache[key] = result
        
        # Update metadata
        self._cacheMetadata[key] = {
            "timestamp": time.time(),
            "last_access": time.time(),
            "size": result_size
        }

        # Update statistics - toujours utiliser la taille du cache
        self._cacheStats["entries"] = len(self._analyzeCache)
        self._cacheStats["size"] += result_size

        # Clean cache if needed
        self._clean_cache()
        
        # Save cache to file
        self._save_cache_to_file()
        
        # Update interface to show new cache size
        try:
            # Use extender reference to update UI
            if self._extender and hasattr(self._extender, "_config_tab"):
                self._extender._config_tab.update_cache_stats()
        except Exception as e:
            self._stdout.write("Error updating cache stats UI: " + str(e) + "\n")

    def _save_cache_to_file(self):
        """Save cache to a file"""
        if not self._cachePath:
            return

        try:
            # Make sure the input counter is up to date before saving.
            self._cacheStats["entries"] = len(self._analyzeCache)
            
            # Create a dictionary with cache data
            cacheData = {
                "cache": self._analyzeCache,
                "metadata": self._cacheMetadata,
                "stats": self._cacheStats
            }

            # Save to JSON file
            with open(self._cachePath, 'w') as f:
                json.dump(cacheData, f)
        except Exception as e:
            # Ignore file write errors
            stdout = None
            try:
                stdout = self._callbacks.getStdout()
                stdout.write("Error saving cache: " + str(e) + "\n")
            except:
                pass

    def clear_cache(self):
        """Clear the cache and reset statistics"""
        self._analyzeCache.clear()
        self._cacheMetadata.clear()
        self._cacheStats["size"] = 0
        self._cacheStats["entries"] = 0

        # Remove cache file if it exists
        if self._cachePath and os.path.exists(self._cachePath):
            try:
                os.remove(self._cachePath)
            except:
                pass
                
        # Update UI
        try:
            if self._extender and hasattr(self._extender, "_config_tab"):
                self._extender._config_tab.update_cache_stats()
        except Exception as e:
            self._stdout.write("Error updating cache stats UI after clear: " + str(e) + "\n")

    def get_cache_stats(self):
        """
        Get formatted cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        # Create a clean copy of stats without the processed_keys set
        stats = {k: v for k, v in self._cacheStats.items() if k != "processed_keys"}
        
        # Add current entries count to ensure consistency
        stats["entries"] = len(self._analyzeCache)

        # Convert size to readable format
        if stats["size"] < 1024:
            size_str = "{0} B".format(stats["size"])
        elif stats["size"] < 1024 * 1024:
            size_str = "{0:.2f} KB".format(stats["size"] / 1024.0)
        else:
            size_str = "{0:.2f} MB".format(stats["size"] / (1024.0 * 1024.0))

        stats["size_str"] = size_str
        
        # Add configuration info
        stats["max_size_mb"] = self._config.get("CACHE_MAX_SIZE_MB", 100)
        stats["max_age_days"] = self._config.get("CACHE_MAX_AGE_DAYS", 30)
        stats["max_entries"] = self._config.get("CACHE_MAX_ENTRIES", 1000)
        
        return stats