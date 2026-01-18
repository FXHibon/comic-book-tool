"""Directory scanning and file discovery."""

import re
from pathlib import Path
from typing import List, Dict, Set

from .file_detector import get_expected_type_from_extension


class ScanResult:
    """Container for scan results."""
    
    def __init__(self):
        self.cbr_files: List[Path] = []
        self.cbz_files: List[Path] = []
        self.image_sequence_dirs: List[Path] = []
    
    def __repr__(self):
        return (f"ScanResult(cbr_files={len(self.cbr_files)}, "
                f"cbz_files={len(self.cbz_files)}, "
                f"image_sequences={len(self.image_sequence_dirs)})")


def scan_directory(directory: Path, recursive: bool = True) -> ScanResult:
    """
    Scan directory for CBR/CBZ files and image sequences.
    
    Args:
        directory: Directory to scan
        recursive: If True, scan subdirectories
        
    Returns:
        ScanResult object containing found files and directories
    """
    result = ScanResult()
    
    if not directory.exists() or not directory.is_dir():
        return result
    
    # Pattern for sequentially numbered images (001.jpg, 002.png, etc.)
    image_pattern = re.compile(r'^0*(\d+)\.(jpg|jpeg|png|gif|bmp|webp)$', re.IGNORECASE)
    
    if recursive:
        iterator = directory.rglob('*')
    else:
        iterator = directory.iterdir()
    
    for item in iterator:
        if item.is_file():
            ext = item.suffix.lower()
            if ext == '.cbr':
                result.cbr_files.append(item)
            elif ext == '.cbz':
                result.cbz_files.append(item)
        elif item.is_dir():
            # Check if directory contains sequentially numbered images
            if _is_image_sequence_directory(item, image_pattern):
                result.image_sequence_dirs.append(item)
    
    return result


def _is_image_sequence_directory(directory: Path, pattern: re.Pattern) -> bool:
    """
    Check if directory contains sequentially numbered images.
    
    Args:
        directory: Directory to check
        pattern: Compiled regex pattern for image files
        
    Returns:
        True if directory appears to contain an image sequence
    """
    image_files = []
    
    try:
        for item in directory.iterdir():
            if item.is_file() and pattern.match(item.name):
                match = pattern.match(item.name)
                if match:
                    number = int(match.group(1))
                    image_files.append((number, item))
    except (PermissionError, OSError):
        return False
    
    if len(image_files) < 2:  # Need at least 2 images to be a sequence
        return False
    
    # Check if numbers are sequential
    image_files.sort(key=lambda x: x[0])
    numbers = [num for num, _ in image_files]
    
    # Check if numbers form a sequence (allowing some gaps)
    # We'll be lenient - if we have at least 3 consecutive numbers, it's a sequence
    consecutive_count = 0
    max_consecutive = 0
    
    for i in range(len(numbers) - 1):
        if numbers[i + 1] == numbers[i] + 1:
            consecutive_count += 1
            max_consecutive = max(max_consecutive, consecutive_count)
        else:
            consecutive_count = 0
    
    # Consider it a sequence if we have at least 3 consecutive numbers
    # or if numbers are mostly sequential (80% of numbers are in sequence)
    if max_consecutive >= 2 or len(set(range(min(numbers), max(numbers) + 1)) & set(numbers)) / len(range(min(numbers), max(numbers) + 1)) > 0.8:
        return True
    
    return False
