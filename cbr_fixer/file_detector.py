"""File type detection by reading file headers."""

from pathlib import Path
from typing import Optional


def detect_file_type(filepath: Path) -> str:
    """
    Detect the actual file type by reading magic bytes.
    
    Args:
        filepath: Path to the file to check
        
    Returns:
        'CBR' if RAR archive, 'CBZ' if ZIP archive, 'UNKNOWN' otherwise
    """
    if not filepath.exists() or not filepath.is_file():
        return 'UNKNOWN'
    
    try:
        with open(filepath, 'rb') as f:
            # Read first 8 bytes to check magic numbers
            header = f.read(8)
            
            if len(header) < 4:
                return 'UNKNOWN'
            
            # Check for RAR format
            # RAR v1.5: "Rar!\x1a\x07\x00" or "Rar!\x1a\x07\x01\x00"
            # RAR v5.0: "Rar!\x1a\x07\x01\x00"
            if header[:4] == b'Rar!' and len(header) >= 7:
                if header[4:7] == b'\x1a\x07\x00':
                    return 'CBR'
                elif len(header) >= 8 and header[4:8] == b'\x1a\x07\x01\x00':
                    return 'CBR'
            
            # Check for ZIP format: "PK\x03\x04" (local file header) or "PK\x05\x06" (empty archive)
            if header[:2] == b'PK':
                if len(header) >= 4:
                    if header[2:4] == b'\x03\x04' or header[2:4] == b'\x05\x06':
                        return 'CBZ'
            
            return 'UNKNOWN'
    except (IOError, OSError):
        return 'UNKNOWN'


def get_expected_type_from_extension(filepath: Path) -> Optional[str]:
    """
    Get expected file type from extension.
    
    Args:
        filepath: Path to the file
        
    Returns:
        'CBR' if .cbr extension, 'CBZ' if .cbz extension, None otherwise
    """
    ext = filepath.suffix.lower()
    if ext == '.cbr':
        return 'CBR'
    elif ext == '.cbz':
        return 'CBZ'
    return None
