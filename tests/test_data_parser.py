"""
Unit tests for data_parser module
"""
import unittest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_parser import DataParser


class TestDataParser(unittest.TestCase):
    """Test cases for DataParser class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.parser = DataParser()
    
    def test_extract_case_ids_valid_data(self):
        """Test extraction with valid case data"""
        test_text = """
        ICM 635658889 - Critical incident
        Support Request Number: 2505160020000588
        Additional details...
        """
        
        result = self.parser.extract_case_ids(test_text)
        
        self.assertEqual(result['icm_id'], '635658889')
        self.assertEqual(result['case_id'], '2505160020000588')
    
    def test_extract_case_ids_alternative_format(self):
        """Test extraction with alternative case ID format"""
        test_text = """
        Case ICM:123456789
        Case ID: 1234567890123456
        """
        
        result = self.parser.extract_case_ids(test_text)
        
        self.assertEqual(result['icm_id'], '123456789')
        self.assertEqual(result['case_id'], '1234567890123456')
    
    def test_extract_case_ids_missing_data(self):
        """Test extraction with missing IDs"""
        test_text = "This is just regular text without case IDs"
        
        result = self.parser.extract_case_ids(test_text)
        
        self.assertIsNone(result['icm_id'])
        self.assertIsNone(result['case_id'])
    
    def test_extract_case_ids_partial_data(self):
        """Test extraction with only one ID present"""
        test_text = "ICM 123456789 but no support case number"
        
        result = self.parser.extract_case_ids(test_text)
        
        self.assertEqual(result['icm_id'], '123456789')
        self.assertIsNone(result['case_id'])
    
    def test_is_valid_case_data(self):
        """Test validation of case data"""
        valid_text = """
        ICM 635658889 - Critical incident
        Support Request Number: 2505160020000588
        """
        
        invalid_text = "Just regular text"
        
        self.assertTrue(self.parser.is_valid_case_data(valid_text))
        self.assertFalse(self.parser.is_valid_case_data(invalid_text))
        self.assertFalse(self.parser.is_valid_case_data(""))
        self.assertFalse(self.parser.is_valid_case_data(None))
    
    def test_generate_filename(self):
        """Test filename generation"""
        test_text = """
        ICM 635658889 - Critical incident
        Support Request Number: 2505160020000588
        """
        
        filename = self.parser.generate_filename(test_text)
        
        self.assertEqual(filename, "635658889_2505160020000588.txt")
    
    def test_generate_filename_invalid_data(self):
        """Test filename generation with invalid data"""
        test_text = "No valid case data here"
        
        filename = self.parser.generate_filename(test_text)
        
        self.assertIsNone(filename)
    
    def test_validate_ids(self):
        """Test ID validation"""
        # Valid IDs
        is_valid, error = self.parser.validate_ids("123456789", "1234567890123456")
        self.assertTrue(is_valid)
        self.assertEqual(error, "")
        
        # Invalid ICM ID (wrong length)
        is_valid, error = self.parser.validate_ids("12345", "1234567890123456")
        self.assertFalse(is_valid)
        self.assertIn("ICM ID must be 9 digits", error)
        
        # Invalid Case ID (too short)
        is_valid, error = self.parser.validate_ids("123456789", "12345")
        self.assertFalse(is_valid)
        self.assertIn("Case ID must be at least 13 digits", error)
        
        # Missing IDs
        is_valid, error = self.parser.validate_ids("", "")
        self.assertFalse(is_valid)
        self.assertIn("ICM ID not found", error)
        self.assertIn("Case ID not found", error)
    
    def test_extract_metadata(self):
        """Test metadata extraction"""
        test_text = """
        ICM 635658889 - Critical incident
        Support Request Number: 2505160020000588
        This is a critical support case
        """
        
        metadata = self.parser.extract_metadata(test_text)
        
        self.assertIn('timestamp', metadata)
        self.assertIn('text_length', metadata)
        self.assertIn('line_count', metadata)
        self.assertIn('icm_id', metadata)
        self.assertIn('case_id', metadata)
        self.assertIn('contains_incident', metadata)
        self.assertIn('contains_critical', metadata)
        self.assertIn('contains_support', metadata)
        
        self.assertEqual(metadata['icm_id'], '635658889')
        self.assertEqual(metadata['case_id'], '2505160020000588')
        self.assertTrue(metadata['contains_incident'])
        self.assertTrue(metadata['contains_critical'])
        self.assertTrue(metadata['contains_support'])


if __name__ == '__main__':
    unittest.main()
