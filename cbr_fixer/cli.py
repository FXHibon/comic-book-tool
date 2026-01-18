"""Main CLI entry point."""

import argparse
import logging
import sys
from pathlib import Path

from .processor import convert_cbr_to_cbz, fix_extension
from .packager import package_to_cbr
from .scanner import scan_directory

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Fix CBR/CBZ file extensions, convert CBR to CBZ, and package image sequences.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/comics
  %(prog)s /path/to/comics --dry-run
  %(prog)s /path/to/comics --no-recursive
        """
    )
    
    parser.add_argument(
        'directory',
        type=Path,
        help='Directory to scan for CBR/CBZ files and image sequences'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making any changes'
    )
    
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        default=True,
        help='Scan subdirectories recursively (default: True)'
    )
    
    parser.add_argument(
        '--no-recursive',
        dest='recursive',
        action='store_false',
        help='Do not scan subdirectories'
    )
    
    args = parser.parse_args()
    
    # Validate directory
    if not args.directory.exists():
        logger.error(f"Directory does not exist: {args.directory}")
        sys.exit(1)
    
    if not args.directory.is_dir():
        logger.error(f"Path is not a directory: {args.directory}")
        sys.exit(1)
    
    # Run the fixer
    try:
        run_fixer(args.directory, args.dry_run, args.recursive)
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


def run_fixer(directory: Path, dry_run: bool, recursive: bool):
    """
    Run the CBR/CBZ fixer on a directory.
    
    Args:
        directory: Directory to process
        dry_run: If True, only show what would be done
        recursive: If True, scan subdirectories
    """
    if dry_run:
        logger.info("=" * 60)
        logger.info("DRY RUN MODE - No files will be modified")
        logger.info("=" * 60)
    
    logger.info(f"Scanning directory: {directory}")
    if recursive:
        logger.info("Recursive mode: enabled")
    else:
        logger.info("Recursive mode: disabled")
    
    # Scan directory
    scan_result = scan_directory(directory, recursive=recursive)
    
    logger.info(f"\nFound:")
    logger.info(f"  - {len(scan_result.cbr_files)} CBR files")
    logger.info(f"  - {len(scan_result.cbz_files)} CBZ files")
    logger.info(f"  - {len(scan_result.image_sequence_dirs)} image sequence directories")
    
    if not scan_result.cbr_files and not scan_result.cbz_files and not scan_result.image_sequence_dirs:
        logger.info("\nNo files to process.")
        return
    
    logger.info("\n" + "=" * 60)
    logger.info("Processing files...")
    logger.info("=" * 60)
    
    # Process CBR files
    fixed_count = 0
    converted_count = 0
    
    for cbr_file in scan_result.cbr_files:
        logger.info(f"\nProcessing CBR file: {cbr_file}")
        
        # Check and fix extension if needed
        fixed_path = fix_extension(cbr_file, dry_run=dry_run)
        if fixed_path:
            fixed_count += 1
            # If extension was fixed (meaning it was actually a CBZ), skip conversion
            continue
        
        # Convert CBR to CBZ (only if it's actually a valid CBR)
        converted_path = convert_cbr_to_cbz(cbr_file, dry_run=dry_run)
        if converted_path:
            converted_count += 1
    
    # Process CBZ files
    for cbz_file in scan_result.cbz_files:
        logger.info(f"\nProcessing CBZ file: {cbz_file}")
        
        # Check and fix extension if needed
        fixed_path = fix_extension(cbz_file, dry_run=dry_run)
        if fixed_path:
            fixed_count += 1
    
    # Package image sequences
    packaged_count = 0
    for img_dir in scan_result.image_sequence_dirs:
        logger.info(f"\nProcessing image sequence directory: {img_dir}")
        packaged_path = package_to_cbr(img_dir, dry_run=dry_run)
        if packaged_path:
            packaged_count += 1
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Summary:")
    logger.info("=" * 60)
    logger.info(f"  - Extension fixes: {fixed_count}")
    logger.info(f"  - CBR to CBZ conversions: {converted_count}")
    logger.info(f"  - Image sequences packaged: {packaged_count}")
    
    if dry_run:
        logger.info("\n" + "=" * 60)
        logger.info("DRY RUN COMPLETE - No files were modified")
        logger.info("Run without --dry-run to apply changes")
        logger.info("=" * 60)


if __name__ == '__main__':
    main()
