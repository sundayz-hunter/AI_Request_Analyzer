# -*- coding: utf-8 -*-

from java.lang import System
import hashlib

def calculate_message_hash(content):
    """
    Calculate a MD5 hash of a message for consistent caching.
    
    Args:
        content: The message content (bytes)
        
    Returns:
        A string hash identifier (MD5)
    """
    if content is None:
        return None

    try:
        # Convert to string if needed
        if not isinstance(content, str):
            message_str = str(content)
        else:
            message_str = content
            
        # Create MD5 hash
        md5_hash = hashlib.md5(message_str.encode('utf-8', errors='replace')).hexdigest()
        return md5_hash
    except:
        # Fallback if hashing fails for any reason
        try:
            length = len(content)
            sample = content[:20] + content[-20:] if length > 40 else content
            return str(length) + "_" + str(sum(bytearray(sample)))
        except:
            return str(System.identityHashCode(content))

def format_size(size_in_bytes):
    """
    Format a size in bytes to a readable string.
    
    Args:
        size_in_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_in_bytes < 1024:
        return "{0} B".format(size_in_bytes)
    elif size_in_bytes < 1024 * 1024:
        return "{0:.2f} KB".format(size_in_bytes / 1024.0)
    else:
        return "{0:.2f} MB".format(size_in_bytes / (1024.0 * 1024.0))


def truncate_message(message, max_length):
    """
    Truncate a message to a maximum length.

    Args:
        message: The message to truncate
        max_length: Maximum length (required)

    Returns:
        Truncated message
    """
    if len(message) <= max_length:
        return message

    truncated = message[:max_length]
    truncated += "...[TRUNCATED - Original length: " + str(len(message)) + " bytes]"
    return truncated