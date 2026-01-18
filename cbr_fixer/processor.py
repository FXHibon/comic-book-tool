"""File processing: fix extensions and convert CBR to CBZ."""

import logging
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Optional

import rarfile

from .file_detector import detect_file_type, get_expected_type_from_extension
from .utils import log_operation

logger = logging.getLogger(__name__)


def fix_extension(filepath: Path, dry_run: bool = False) -> Optional[Path]:
    """
    Fix file extension if it doesn't match the actual file type.
    
    Args:
        filepath: Path to the file to check and fix
        dry_run: If True, only log what would be done
        
    Returns:
        Path to the new file with corrected extension, or None if no fix needed or error
    """
    expected_type = get_expected_type_from_extension(filepath)
    if expected_type is None:
        return None
    
    actual_type = detect_file_type(filepath)
    
    if actual_type == 'UNKNOWN':
        logger.warning(f"Could not determine file type for: {filepath}")
        return None
    
    if expected_type == actual_type:
        # Extension matches actual type, no fix needed
        return None
    
    # Extension doesn't match - need to fix
    if actual_type == 'CBR':
        new_extension = '.cbr'
    elif actual_type == 'CBZ':
        new_extension = '.cbz'
    else:
        return None
    
    # Create new filename with correct extension
    new_path = filepath.with_suffix(new_extension)
    
    if dry_run:
        log_operation(f"Would fix extension: {filepath} -> {new_path} (actual type: {actual_type})", dry_run=True)
        return new_path
    
    try:
        shutil.copy2(filepath, new_path)
        log_operation(f"Fixed extension: {filepath} -> {new_path} (actual type: {actual_type})", dry_run=False)
        return new_path
    except (IOError, OSError) as e:
        logger.error(f"Error fixing extension for {filepath}: {e}")
        return None


def convert_cbr_to_cbz(cbr_path: Path, dry_run: bool = False) -> Optional[Path]:
    """
    Convert a CBR (RAR) file to CBZ (ZIP) format.
    
    Args:
        cbr_path: Path to the CBR file
        dry_run: If True, only log what would be done
        
    Returns:
        Path to the new CBZ file, or None on error
    """
    if not cbr_path.exists():
        logger.error(f"CBR file not found: {cbr_path}")
        return None
    
    # Verify it's actually a RAR file
    actual_type = detect_file_type(cbr_path)
    if actual_type != 'CBR':
        logger.warning(f"File {cbr_path} is not a valid CBR (RAR) file, actual type: {actual_type}")
        return None
    
    cbz_path = cbr_path.with_suffix('.cbz')
    
    if dry_run:
        log_operation(f"Would convert CBR to CBZ: {cbr_path} -> {cbz_path}", dry_run=True)
        return cbz_path
    
    try:
        # Extract RAR contents to temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Extract RAR archive
            try:
                with rarfile.RarFile(cbr_path) as rf:
                    rf.extractall(tmpdir_path)
            except rarfile.RarCannotExec:
                logger.error(f"Cannot extract RAR file. Make sure 'unrar' is installed and in PATH.")
                return None
            except Exception as e:
                logger.error(f"Error extracting RAR file {cbr_path}: {e}")
                return None
            
            # Create ZIP archive from extracted files
            with zipfile.ZipFile(cbz_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                # Get all files from temp directory, maintaining directory structure
                for file_path in sorted(tmpdir_path.rglob('*')):
                    if file_path.is_file():
                        # Use relative path from temp directory root
                        arcname = file_path.relative_to(tmpdir_path)
                        zf.write(file_path, arcname)
        
        log_operation(f"Converted CBR to CBZ: {cbr_path} -> {cbz_path}", dry_run=False)
        return cbz_path
    except Exception as e:
        logger.error(f"Error converting {cbr_path} to CBZ: {e}")
        return None
