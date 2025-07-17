"""
Data parser for extracting case IDs from clipboard content
"""
import re
from typing import Dict, Optional, Tuple
from datetime import datetime


class DataParser:
    """Parser for extracting ICM and Support Case IDs from text"""
    
    # Regex patterns for ID extraction
    PATTERNS = {
        'icm_id': re.compile(r"ICM.*?(\d{9})", re.IGNORECASE),
        'case_id': re.compile(r"Support Request Number:\s*(\d{13,})", re.IGNORECASE),
        'alternative_case': re.compile(r"Case[:\s#]*(\d{13,})", re.IGNORECASE),
        'simple_case': re.compile(r"\b(\d{13,})\b"),  # Any 13+ digit number
        'cri_pattern': re.compile(r"CRI[:\s]*(\d{13,})", re.IGNORECASE)
    }
    
    def __init__(self):
        """Initialize data parser"""
        pass
    
    def extract_case_ids(self, text: str) -> Dict[str, Optional[str]]:
        """Extract ICM and Support Case IDs from clipboard text
        
        Args:
            text (str): Clipboard content
            
        Returns:
            Dict[str, Optional[str]]: Dictionary with 'icm_id' and 'case_id' keys
        """
        if not text or not isinstance(text, str):
            return {'icm_id': None, 'case_id': None}
        
        results = {}
        
        # Extract ICM ID
        icm_match = self.PATTERNS['icm_id'].search(text)
        results['icm_id'] = icm_match.group(1) if icm_match else None
        
        # Extract Support Case ID (try multiple patterns in order of specificity)
        case_id = None
        
        # Primary pattern: "Support Request Number: ..."
        case_match = self.PATTERNS['case_id'].search(text)
        if case_match:
            case_id = case_match.group(1)
        else:
            # Alternative pattern: "Case: ..." or "Case #..."
            alt_match = self.PATTERNS['alternative_case'].search(text)
            if alt_match:
                case_id = alt_match.group(1)
            else:
                # CRI pattern: "CRI: ..."
                cri_match = self.PATTERNS['cri_pattern'].search(text)
                if cri_match:
                    case_id = cri_match.group(1)
                else:
                    # Simple pattern: any 13+ digit number
                    simple_match = self.PATTERNS['simple_case'].search(text)
                    if simple_match:
                        case_id = simple_match.group(1)
        
        results['case_id'] = case_id
        return results
    
    def is_valid_case_data(self, text: str) -> bool:
        """Check if text contains valid case review data
        
        Args:
            text (str): Text to validate
            
        Returns:
            bool: True if text contains ICM ID or Case ID (or both)
        """
        if not text:
            return False
        
        ids = self.extract_case_ids(text)
        return ids['icm_id'] is not None or ids['case_id'] is not None
    
    def generate_filename(self, text: str) -> Optional[str]:
        """Generate filename from extracted IDs
        
        Args:
            text (str): Text containing case data
            
        Returns:
            Optional[str]: Generated filename or None if no IDs found
        """
        ids = self.extract_case_ids(text)
        
        if ids['icm_id'] and ids['case_id']:
            return f"{ids['icm_id']}_{ids['case_id']}.txt"
        elif ids['icm_id']:
            return f"ICM_{ids['icm_id']}.txt"
        elif ids['case_id']:
            return f"Case_{ids['case_id']}.txt"
        
        return None
    
    def validate_ids(self, icm_id: str, case_id: str) -> Tuple[bool, str]:
        """Validate extracted IDs
        
        Args:
            icm_id (str): ICM ID to validate
            case_id (str): Case ID to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        errors = []
        
        # Validate ICM ID (should be 9 digits)
        if not icm_id:
            errors.append("ICM ID not found")
        elif not icm_id.isdigit() or len(icm_id) != 9:
            errors.append("ICM ID must be 9 digits")
        
        # Validate Case ID (should be 13+ digits)
        if not case_id:
            errors.append("Case ID not found")
        elif not case_id.isdigit() or len(case_id) < 13:
            errors.append("Case ID must be at least 13 digits")
        
        is_valid = len(errors) == 0
        error_message = "; ".join(errors) if errors else ""
        
        return is_valid, error_message
    
    def extract_metadata(self, text: str) -> Dict[str, any]:
        """Extract additional metadata from case data
        
        Args:
            text (str): Case data text
            
        Returns:
            Dict[str, any]: Metadata dictionary
        """
        metadata = {
            'timestamp': datetime.now().isoformat(),
            'text_length': len(text) if text else 0,
            'line_count': len(text.splitlines()) if text else 0
        }
        
        # Add extracted IDs
        ids = self.extract_case_ids(text)
        metadata.update(ids)
        
        # Check for common case data patterns
        if text:
            metadata['contains_incident'] = 'incident' in text.lower()
            metadata['contains_critical'] = 'critical' in text.lower()
            metadata['contains_support'] = 'support' in text.lower()
        
        return metadata
