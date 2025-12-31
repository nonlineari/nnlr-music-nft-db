#!/usr/bin/env python3
"""Script to index local music files into the database."""

import os
import sys
import hashlib
import mimetypes
from pathlib import Path
from typing import List, Tuple

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from database import get_database


def calculate_file_hash(file_path: str) -> str:
    """Calculate SHA256 hash of file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Hexadecimal hash string
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def get_music_files(directory: str, extensions: List[str] = None) -> List[str]:
    """Recursively find music files in directory.
    
    Args:
        directory: Root directory to search
        extensions: List of file extensions to include (e.g., ['.mp3', '.wav'])
        
    Returns:
        List of file paths
    """
    if extensions is None:
        extensions = ['.mp3', '.wav', '.flac', '.aac', '.m4a', '.ogg', '.wma']
    
    music_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.lower().endswith(ext) for ext in extensions):
                music_files.append(os.path.join(root, file))
    
    return music_files


def index_file(db_conn, file_path: str) -> Tuple[bool, str]:
    """Index a single file into the database.
    
    Args:
        db_conn: Database connection
        file_path: Path to the file
        
    Returns:
        Tuple of (success, message)
    """
    try:
        # Get file info
        file_stat = os.stat(file_path)
        file_name = os.path.basename(file_path)
        file_size = file_stat.st_size
        mime_type, _ = mimetypes.guess_type(file_path)
        
        # Calculate hash
        file_hash = calculate_file_hash(file_path)
        
        # Check if file already exists
        cursor = db_conn.cursor()
        cursor.execute("SELECT id FROM music_files WHERE file_hash = ?", (file_hash,))
        existing = cursor.fetchone()
        
        if existing:
            return False, f"File already indexed: {file_name}"
        
        # Insert into database
        cursor.execute("""
            INSERT INTO music_files (file_path, file_name, file_size, file_hash, mime_type)
            VALUES (?, ?, ?, ?, ?)
        """, (file_path, file_name, file_size, file_hash, mime_type))
        
        db_conn.commit()
        return True, f"Indexed: {file_name}"
        
    except Exception as e:
        return False, f"Error indexing {file_path}: {str(e)}"


def main():
    """Main indexing function."""
    if len(sys.argv) < 2:
        print("Usage: python index_files.py <directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory")
        sys.exit(1)
    
    print(f"Indexing music files from: {directory}")
    
    # Initialize database
    db = get_database()
    db.initialize_schema()
    
    # Find and index files
    music_files = get_music_files(directory)
    print(f"Found {len(music_files)} music files")
    
    indexed_count = 0
    skipped_count = 0
    
    with db as conn:
        for file_path in music_files:
            success, message = index_file(conn, file_path)
            print(message)
            if success:
                indexed_count += 1
            else:
                skipped_count += 1
    
    print(f"\nIndexing complete!")
    print(f"Indexed: {indexed_count} files")
    print(f"Skipped: {skipped_count} files")


if __name__ == "__main__":
    main()
