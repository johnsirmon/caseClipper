#!/usr/bin/env python3
"""
Simple test script for CaseClipSaver
Tests the core functionality without GUI
"""

import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from caseclipsaver import Config, DataParser, FileManager

def test_data_parser():
    """Test data parser functionality"""
    print("Testing DataParser...")
    
    parser = DataParser()
    
    # Test cases
    test_cases = [
        {
            'text': 'ICM 635658889 - Critical incident\nSupport Request Number: 2505160020000588',
            'expected_icm': '635658889',
            'expected_case': '2505160020000588'
        },
        {
            'text': 'ICM:123456789 Case: 1234567890123456',
            'expected_icm': '123456789',
            'expected_case': '1234567890123456'
        },
        {
            'text': 'No valid data here',
            'expected_icm': None,
            'expected_case': None
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\nTest case {i+1}:")
        print(f"Text: {test_case['text']}")
        
        ids = parser.extract_case_ids(test_case['text'])
        print(f"Extracted ICM ID: {ids['icm_id']}")
        print(f"Extracted Case ID: {ids['case_id']}")
        
        is_valid = parser.is_valid_case_data(test_case['text'])
        print(f"Is valid case data: {is_valid}")
        
        filename = parser.generate_filename(test_case['text'])
        print(f"Generated filename: {filename}")
        
        # Check results
        if ids['icm_id'] == test_case['expected_icm'] and ids['case_id'] == test_case['expected_case']:
            print("✓ PASS")
        else:
            print("✗ FAIL")
            print(f"Expected ICM: {test_case['expected_icm']}, got: {ids['icm_id']}")
            print(f"Expected Case: {test_case['expected_case']}, got: {ids['case_id']}")

def test_file_manager():
    """Test file manager functionality"""
    print("\n\nTesting FileManager...")
    
    config = Config()
    file_manager = FileManager(config)
    
    # Test content
    test_content = "ICM 635658889 - Test incident\nSupport Request Number: 2505160020000588\nTest content for file manager"
    test_filename = "test_635658889_2505160020000588.txt"
    
    print(f"Testing file save...")
    print(f"Content length: {len(test_content)}")
    print(f"Filename: {test_filename}")
    
    success, message = file_manager.save_case_data(test_content, test_filename)
    print(f"Save result: {success}")
    print(f"Message: {message}")
    
    if success:
        print("✓ File save test PASSED")
        
        # Test with metadata
        metadata = {
            'timestamp': '2024-01-01T12:00:00',
            'icm_id': '635658889',
            'case_id': '2505160020000588'
        }
        
        success2, message2 = file_manager.save_with_metadata(test_content, "test_with_metadata.txt", metadata)
        print(f"Save with metadata result: {success2}")
        print(f"Message: {message2}")
        
        if success2:
            print("✓ Metadata save test PASSED")
        else:
            print("✗ Metadata save test FAILED")
    else:
        print("✗ File save test FAILED")

def test_config():
    """Test configuration loading"""
    print("\n\nTesting Config...")
    
    config = Config()
    
    print(f"Output directory: {config.output_directory}")
    print(f"Polling interval: {config.polling_interval}")
    print(f"File encoding: {config.file_encoding}")
    print(f"Enable notifications: {config.enable_notifications}")
    print(f"Auto create directory: {config.auto_create_directory}")
    print(f"Max file size MB: {config.max_file_size_mb}")
    
    print("✓ Config test PASSED")

def main():
    """Run all tests"""
    print("CaseClipSaver - Simple Test Suite")
    print("=" * 40)
    
    try:
        test_config()
        test_data_parser()
        test_file_manager()
        
        print("\n" + "=" * 40)
        print("All tests completed!")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()