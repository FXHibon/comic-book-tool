"""Package image sequences into CBR files."""

import logging
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional

from .utils import log_operation

logger = logging.getLogger(__name__)


def detect_image_sequence(directory: Path) -> Optional[List[Path]]:
    """
    Detect if directory contains sequentially numbered images.
    
    Args:
        directory: Directory to check
        
    Returns:
        List of image file paths in numerical order, or None if not a sequence
    """
    if not directory.exists() or not directory.is_dir():
        return None
    
    # Pattern for sequentially numbered images
    pattern = re.compile(r'^0*(\d+)\.(jpg|jpeg|png|gif|bmp|webp)$', re.IGNORECASE)
    
    image_files = []
    
    try:
        for item in directory.iterdir():
            if item.is_file() and pattern.match(item.name):
                match = pattern.match(item.name)
                if match:
                    number = int(match.group(1))
                    image_files.append((number, item))
    except (PermissionError, OSError) as e:
        logger.warning(f"Error reading directory {directory}: {e}")
        return None
    
    if len(image_files) < 2:
        return None
    
    # Sort by number
    image_files.sort(key=lambda x: x[0])
    numbers = [num for num, _ in image_files]
    
    # Check if numbers form a reasonable sequence
    # Allow some gaps but require at least 3 consecutive numbers or 80% coverage
    consecutive_count = 0
    max_consecutive = 0
    
    for i in range(len(numbers) - 1):
        if numbers[i + 1] == numbers[i] + 1:
            consecutive_count += 1
            max_consecutive = max(max_consecutive, consecutive_count)
        else:
            consecutive_count = 0
    
    min_num = min(numbers)
    max_num = max(numbers)
    expected_range = set(range(min_num, max_num + 1))
    actual_numbers = set(numbers)
    coverage = len(expected_range & actual_numbers) / len(expected_range) if expected_range else 0
    
    if max_consecutive >= 2 or coverage > 0.8:
        return [path for _, path in image_files]
    
    return None


def package_to_cbr(directory: Path, dry_run: bool = False) -> Optional[Path]:
    """
    Package a directory of sequentially numbered images into a CBR file.
    
    Args:
        directory: Directory containing image sequence
        dry_run: If True, only log what would be done
        
    Returns:
        Path to the created CBR file, or None on error
    """
    image_files = detect_image_sequence(directory)
    if not image_files:
        logger.warning(f"Directory {directory} does not contain a valid image sequence")
        return None
    
    # Create CBR filename based on directory name
    cbr_filename = f"{directory.name}.cbr"
    cbr_path = directory.parent / cbr_filename
    
    # If file already exists, add a suffix
    counter = 1
    original_path = cbr_path
    while cbr_path.exists():
        cbr_path = original_path.parent / f"{directory.name}_{counter}.cbr"
        counter += 1
    
    if dry_run:
        log_operation(f"Would package image sequence from {directory} -> {cbr_path}", dry_run=True)
        log_operation(f"  Would include {len(image_files)} images", dry_run=True)
        return cbr_path
    
    try:
        # Create RAR archive using rar command or unrar
        # Since rarfile doesn't support creating RAR files, we use subprocess
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Copy images to temp directory (maintaining order)
            for img_path in image_files:
                shutil.copy2(img_path, tmpdir_path / img_path.name)
            
            # Try to use 'rar' command first
            # Use shell=True on Windows, but prefer explicit file list on Unix
            try:
                # Find rar command in PATH
                rar_cmd_path = shutil.which('rar')
                if not rar_cmd_path:
                    raise FileNotFoundError("rar command not found in PATH")
                
                # Build command with explicit file list for better cross-platform support
                rar_cmd = [rar_cmd_path, 'a', '-ep1', str(cbr_path)]
                # Add all image files explicitly
                for img_file in sorted(tmpdir_path.iterdir()):
                    if img_file.is_file():
                        rar_cmd.append(str(img_file))
                
                result = subprocess.run(
                    rar_cmd,
                    check=True,
                    capture_output=True,
                    text=True
                )
            except FileNotFoundError as e:
                logger.error(f"'rar' command not found: {e}")
                logger.error("Please install RAR (rar command) to create CBR files.")
                logger.error("On macOS: brew install rar")
                logger.error("On Linux: apt-get install rar or yum install rar")
                return None
            except subprocess.CalledProcessError as e:
                logger.error(f"Error running rar command: {e}")
                logger.error(f"rar stderr: {e.stderr}")
                return None
        
        log_operation(f"Packaged image sequence: {directory} -> {cbr_path} ({len(image_files)} images)", dry_run=False)
        return cbr_path
    except Exception as e:
        logger.error(f"Error packaging {directory} to CBR: {e}")
        return None
