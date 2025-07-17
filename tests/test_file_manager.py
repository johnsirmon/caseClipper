"""
Unit tests for file_manager module
"""
import unittest
import tempfile
import shutil
import os
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import config
import file_manager

from config import Config
from file_manager import FileManager


class TestFileManager(unittest.TestCase):
    """Test cases for FileManager class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        
        # Create test config
        self.config = Config()
        self.config.config['output_directory'] = self.test_dir
        
        # Create file manager
        self.file_manager = FileManager(self.config)
    
    def tearDown(self):
        """Clean up test fixtures"""
        # Remove temporary directory
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_ensure_output_directory(self):
        """Test output directory creation"""
        # Remove test directory
        shutil.rmtree(self.test_dir, ignore_errors=True)
        
        # Ensure directory is created
        result = self.file_manager.ensure_output_directory()
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.test_dir))
    
    def test_save_case_data(self):
        """Test saving case data to file"""
        content = "Test case data content"
        filename = "test_case.txt"
        
        success, message = self.file_manager.save_case_data(content, filename)
        
        self.assertTrue(success)
        self.assertIn("Saved to:", message)
        
        # Check file exists and has correct content
        file_path = Path(self.test_dir) / filename
        self.assertTrue(file_path.exists())
        
        with open(file_path, 'r', encoding='utf-8') as f:
            saved_content = f.read()
        
        self.assertEqual(saved_content, content)
    
    def test_save_duplicate_file(self):
        """Test handling of duplicate filenames"""
        content1 = "First content"
        content2 = "Second content"
        filename = "duplicate_test.txt"
        
        # Save first file
        success1, message1 = self.file_manager.save_case_data(content1, filename)
        self.assertTrue(success1)
        
        # Save second file with same name
        success2, message2 = self.file_manager.save_case_data(content2, filename)
        self.assertTrue(success2)
        
        # Check both files exist
        original_file = Path(self.test_dir) / filename
        self.assertTrue(original_file.exists())
        
        # Check that timestamp was added to duplicate
        files = list(Path(self.test_dir).glob("duplicate_test*.txt"))
        self.assertEqual(len(files), 2)
    
    def test_save_with_metadata(self):
        """Test saving content with metadata"""
        content = "Test content"
        filename = "metadata_test.txt"
        metadata = {"test_key": "test_value", "number": 42}
        
        success, message = self.file_manager.save_with_metadata(content, filename, metadata)
        
        self.assertTrue(success)
        
        # Check both files exist
        content_file = Path(self.test_dir) / filename
        metadata_file = Path(self.test_dir) / "metadata_test_metadata.json"
        
        self.assertTrue(content_file.exists())
        self.assertTrue(metadata_file.exists())
    
    def test_file_exists(self):
        """Test file existence check"""
        filename = "exists_test.txt"
        
        # File doesn't exist initially
        self.assertFalse(self.file_manager.file_exists(filename))
        
        # Create file
        self.file_manager.save_case_data("test", filename)
        
        # File should exist now
        self.assertTrue(self.file_manager.file_exists(filename))
    
    def test_get_file_path(self):
        """Test getting file path"""
        filename = "path_test.txt"
        expected_path = Path(self.test_dir) / filename
        
        result_path = self.file_manager.get_file_path(filename)
        
        self.assertEqual(result_path, expected_path)
    
    def test_list_case_files(self):
        """Test listing case files"""
        # Create test files
        test_files = ["case1.txt", "case2.txt", "case3.txt"]
        
        for filename in test_files:
            self.file_manager.save_case_data(f"Content for {filename}", filename)
        
        # List files
        files = self.file_manager.list_case_files()
        
        # Check correct number of files returned
        self.assertEqual(len(files), len(test_files))
        
        # Check all files are in the list
        file_names = [f.name for f in files]
        for filename in test_files:
            self.assertIn(filename, file_names)
    
    def test_get_file_info(self):
        """Test getting file information"""
        filename = "info_test.txt"
        content = "Test content for info"
        
        # Save file
        self.file_manager.save_case_data(content, filename)
        
        # Get file info
        info = self.file_manager.get_file_info(filename)
        
        self.assertIsNotNone(info)
        self.assertEqual(info['filename'], filename)
        self.assertTrue(info['exists'])
        self.assertGreater(info['size'], 0)
        self.assertIn('created', info)
        self.assertIn('modified', info)
    
    def test_get_file_info_nonexistent(self):
        """Test getting info for non-existent file"""
        info = self.file_manager.get_file_info("nonexistent.txt")
        self.assertIsNone(info)


if __name__ == '__main__':
    unittest.main()
