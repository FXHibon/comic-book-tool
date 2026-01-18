# CBR/CBZ Fixer

A CLI tool to fix and convert comic book archive files (CBR/CBZ).

## Features

- **Fix file extensions**: Automatically detects if a CBR file is actually a CBZ (or vice versa) and creates a corrected version
- **Convert CBR to CBZ**: Converts all valid CBR (RAR) files to CBZ (ZIP) format
- **Package image sequences**: Detects directories with sequentially numbered images (001.jpg, 002.jpg, etc.) and packages them into CBR files
- **Dry-run mode**: Preview what would be done without making any changes
- **Safe operations**: Never modifies or deletes original files

## Installation

### Prerequisites

- Python 3.8 or higher
- `unrar` command-line tool (for reading RAR/CBR files)
- `rar` command-line tool (for creating RAR/CBR files)

#### Installing unrar and rar

**macOS:**
```bash
brew install unrar rar
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install unrar rar
```

**Linux (Fedora/RHEL):**
```bash
sudo yum install unrar rar
```

### Install the tool

```bash
pip install -e .
```

Or install directly:
```bash
pip install -r requirements.txt
```

## Usage

### Basic usage

Scan a directory and fix/convert files:
```bash
cbr-fixer /path/to/comics
```

### Dry-run mode

Preview what would be done without making changes:
```bash
cbr-fixer /path/to/comics --dry-run
```

### Non-recursive scan

Only scan the specified directory (not subdirectories):
```bash
cbr-fixer /path/to/comics --no-recursive
```

### Help

```bash
cbr-fixer --help
```

## What it does

1. **Scans** the specified directory (and subdirectories by default)
2. **Fixes extensions**: If a `.cbr` file is actually a ZIP archive, creates a `.cbz` version (and vice versa)
3. **Converts CBR to CBZ**: Converts all valid CBR files to CBZ format (creates new files, originals remain)
4. **Packages image sequences**: If a directory contains sequentially numbered images (001.jpg, 002.jpg, etc.), packages them into a CBR file

## Important Notes

- **Original files are never modified or deleted** - all operations create new files
- The tool requires `unrar` to read CBR files and `rar` to create CBR files
- Image sequences must have at least 2 images with sequential numbering
- Supported image formats: jpg, jpeg, png, gif, bmp, webp

## Examples

```bash
# Preview changes
cbr-fixer ~/Comics --dry-run

# Apply changes
cbr-fixer ~/Comics

# Process only current directory
cbr-fixer ~/Comics --no-recursive
```

## License

MIT
