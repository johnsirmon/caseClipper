"""
File manager for handling case data file operations
"""
import os
import json
from typing import Optional, Tuple
from datetime import datetime
from pathlib import Path

try:
    from .config import Config
except ImportError:
    from config import Config


class FileManager:
    """Manages file operations for case data"""
    
    def __init__(self, config: Config):
        """Initialize file manager
        
        Args:
            config (Config): Application configuration
        """
        self.config = config
        self.output_dir = Path(config.output_directory)
        
        # Ensure output directory exists if auto-create is enabled
        if config.auto_create_directory:
            self.ensure_output_directory()
    
    def ensure_output_directory(self) -> bool:
        """Ensure output directory exists
        
        Returns:
            bool: True if directory exists or was created successfully
        """
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating output directory: {e}")
            return False
    
    def save_case_data(self, content: str, filename: str) -> Tuple[bool, str]:
        """Save case data to file
        
        Args:
            content (str): Content to save
            filename (str): Filename to use
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            if not self.ensure_output_directory():
                return False, "Could not create output directory"
            
            file_path = self.output_dir / filename
            
            # Handle duplicate files by appending timestamp
            if file_path.exists():
                base_name = file_path.stem
                extension = file_path.suffix
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_filename = f"{base_name}_{timestamp}{extension}"
                file_path = self.output_dir / new_filename
            
            # Write content to file
            with open(file_path, 'w', encoding=self.config.file_encoding) as f:
                f.write(content)
            
            return True, f"Saved to: {file_path}"
            
        except Exception as e:
            error_msg = f"Error saving file: {e}"
            print(error_msg)
            return False, error_msg
    
    def save_with_metadata(self, content: str, filename: str, metadata: dict) -> Tuple[bool, str]:
        """Save case data with metadata
        
        Args:
            content (str): Content to save
            filename (str): Filename to use
            metadata (dict): Metadata to include
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            # Save main content file
            success, message = self.save_case_data(content, filename)
            if not success:
                return success, message
            
            # Save metadata file
            metadata_filename = filename.replace('.txt', '_metadata.json')
            metadata_path = self.output_dir / metadata_filename
            
            with open(metadata_path, 'w', encoding=self.config.file_encoding) as f:
                json.dump(metadata, f, indent=2)
            
            return True, f"Saved content and metadata: {self.output_dir / filename}"
            
        except Exception as e:
            error_msg = f"Error saving file with metadata: {e}"
            print(error_msg)
            return False, error_msg
    
    def file_exists(self, filename: str) -> bool:
        """Check if file already exists
        
        Args:
            filename (str): Filename to check
            
        Returns:
            bool: True if file exists
        """
        file_path = self.output_dir / filename
        return file_path.exists()
    
    def get_file_path(self, filename: str) -> Path:
        """Get full path for filename
        
        Args:
            filename (str): Filename
            
        Returns:
            Path: Full file path
        """
        return self.output_dir / filename
    
    def list_case_files(self) -> list:
        """List all case files in output directory
        
        Returns:
            list: List of case file paths
        """
        try:
            if not self.output_dir.exists():
                return []
            
            case_files = []
            for file_path in self.output_dir.glob("*.txt"):
                # Skip metadata files
                if not file_path.name.endswith("_metadata.json"):
                    case_files.append(file_path)
            
            return sorted(case_files, key=lambda x: x.stat().st_mtime, reverse=True)
            
        except Exception as e:
            print(f"Error listing case files: {e}")
            return []
    
    def get_file_info(self, filename: str) -> Optional[dict]:
        """Get file information
        
        Args:
            filename (str): Filename to get info for
            
        Returns:
            Optional[dict]: File information or None if file doesn't exist
        """
        try:
            file_path = self.output_dir / filename
            if not file_path.exists():
                return None
            
            stat = file_path.stat()
            return {
                'filename': filename,
                'full_path': str(file_path),
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'exists': True
            }
            
        except Exception as e:
            print(f"Error getting file info: {e}")
            return None
    
    def cleanup_old_files(self, days_old: int = 30) -> Tuple[int, str]:
        """Clean up files older than specified days
        
        Args:
            days_old (int): Number of days old to consider for cleanup
            
        Returns:
            Tuple[int, str]: (files_removed, message)
        """
        try:
            if not self.output_dir.exists():
                return 0, "Output directory does not exist"
            
            cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
            files_removed = 0
            
            for file_path in self.output_dir.glob("*.txt"):
                if file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    files_removed += 1
                    
                    # Also remove associated metadata file if it exists
                    metadata_file = file_path.with_suffix('.json').with_name(
                        file_path.stem + '_metadata.json'
                    )
                    if metadata_file.exists():
                        metadata_file.unlink()
            
            return files_removed, f"Removed {files_removed} old files"
            
        except Exception as e:
            error_msg = f"Error during cleanup: {e}"
            print(error_msg)
            return 0, error_msg
