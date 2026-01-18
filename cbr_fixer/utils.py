"""Utility functions for file operations with dry-run support."""

import logging
import shutil
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


def safe_copy(src: Path, dst: Path, dry_run: bool = False) -> bool:
    """
    Copy a file with dry-run support.
    
    Args:
        src: Source file path
        dst: Destination file path
        dry_run: If True, only log what would be done
        
    Returns:
        True if successful (or dry-run), False on error
    """
    if dry_run:
        logger.info(f"[DRY RUN] Would copy: {src} -> {dst}")
        return True
    
    try:
        shutil.copy2(src, dst)
        logger.info(f"Copied: {src} -> {dst}")
        return True
    except (IOError, OSError) as e:
        logger.error(f"Error copying {src} to {dst}: {e}")
        return False


def safe_create_archive(files: List[Path], archive_path: Path, archive_type: str, dry_run: bool = False) -> bool:
    """
    Create an archive with dry-run support.
    
    Args:
        files: List of file paths to include in archive
        archive_path: Path for the output archive
        archive_type: 'CBR' (RAR) or 'CBZ' (ZIP)
        dry_run: If True, only log what would be done
        
    Returns:
        True if successful (or dry-run), False on error
    """
    if dry_run:
        logger.info(f"[DRY RUN] Would create {archive_type} archive: {archive_path}")
        for f in files:
            logger.info(f"  [DRY RUN] Would add: {f}")
        return True
    
    try:
        if archive_type == 'CBZ':
            import zipfile
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for file_path in files:
                    zf.write(file_path, file_path.name)
            logger.info(f"Created CBZ archive: {archive_path}")
            return True
        elif archive_type == 'CBR':
            import rarfile
            # Note: rarfile doesn't support creating RAR files directly
            # We'll need to use a different approach - call unrar command or use patoolib
            # For now, we'll use a workaround with patoolib or subprocess
            import subprocess
            import tempfile
            
            # Create a temporary directory and copy files there
            with tempfile.TemporaryDirectory() as tmpdir:
                tmpdir_path = Path(tmpdir)
                for file_path in files:
                    shutil.copy2(file_path, tmpdir_path / file_path.name)
                
                # Use rar command if available, otherwise try unrar
                # This is a simplified approach - in production you might want to use patoolib
                try:
                    subprocess.run(
                        ['rar', 'a', '-ep1', str(archive_path), str(tmpdir_path / '*')],
                        check=True,
                        capture_output=True
                    )
                except (subprocess.CalledProcessError, FileNotFoundError):
                    # Try unrar or alternative method
                    logger.warning(f"rar command not found, trying alternative method")
                    # Fallback: we could use patoolib here
                    raise NotImplementedError("RAR creation requires 'rar' command or patoolib")
            
            logger.info(f"Created CBR archive: {archive_path}")
            return True
        else:
            logger.error(f"Unknown archive type: {archive_type}")
            return False
    except Exception as e:
        logger.error(f"Error creating {archive_type} archive {archive_path}: {e}")
        return False


def log_operation(message: str, dry_run: bool = False):
    """Log an operation with dry-run prefix if applicable."""
    prefix = "[DRY RUN] " if dry_run else ""
    logger.info(f"{prefix}{message}")
