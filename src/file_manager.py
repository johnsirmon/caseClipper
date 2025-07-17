"""
File manager for handling case data file operations
"""
import os
import json
import asyncio
from typing import Optional, Tuple
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import threading

try:
    from .config import Config
    from .context_processor import ContextProcessor
    from .logger import get_logger
except ImportError:
    from config import Config
    from context_processor import ContextProcessor
    from logger import get_logger


class FileManager:
    """Manages file operations for case data"""
    
    def __init__(self, config: Config):
        """Initialize file manager
        
        Args:
            config (Config): Application configuration
        """
        self.config = config
        self.output_dir = Path(config.output_directory)
        self.context_processor = ContextProcessor(config)
        self.logger = get_logger(config)
        
        # Thread pool for async operations
        self.thread_pool = ThreadPoolExecutor(max_workers=3)
        
        # File operation lock to prevent race conditions
        self.file_lock = threading.Lock()
        
        # Ensure output directory exists if auto-create is enabled
        if config.auto_create_directory:
            self.ensure_output_directory()
    
    def ensure_output_directory(self) -> bool:
        """Ensure output directory exists
        
        Returns:
            bool: True if directory exists or was created successfully
        """
        try:
            with self.file_lock:
                self.output_dir.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Output directory ensured: {self.output_dir}")
                return True
        except Exception as e:
            self.logger.error(f"Error creating output directory: {e}")
            return False
    
    def save_case_data(self, content: str, filename: str) -> Tuple[bool, str]:
        """Save case data to file with thread safety
        
        Args:
            content (str): Content to save
            filename (str): Filename to use
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            # Validate content size
            if len(content) > self.config.max_file_size_mb * 1024 * 1024:
                error_msg = f"Content too large: {len(content)} bytes exceeds limit"
                self.logger.warning(error_msg)
                return False, error_msg
            
            if not self.ensure_output_directory():
                return False, "Could not create output directory"
            
            with self.file_lock:
                file_path = self.output_dir / filename
                
                # Handle duplicate files by appending timestamp
                if file_path.exists():
                    base_name = file_path.stem
                    extension = file_path.suffix
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    new_filename = f"{base_name}_{timestamp}{extension}"
                    file_path = self.output_dir / new_filename
                
                # Write content to file atomically
                temp_file = file_path.with_suffix('.tmp')
                with open(temp_file, 'w', encoding=self.config.file_encoding) as f:
                    f.write(content)
                
                # Atomic rename
                temp_file.replace(file_path)
                
                self.logger.info(f"Saved file: {file_path}")
                return True, f"Saved to: {file_path}"
            
        except Exception as e:
            error_msg = f"Error saving file: {e}"
            self.logger.error(error_msg)
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
            self.logger.error(error_msg)
            return False, error_msg
    
    def save_enhanced_case_data(self, content: str, filename: str, metadata: dict) -> Tuple[bool, str]:
        """Save case data with enhanced context processing (async)
        
        Args:
            content (str): Content to save
            filename (str): Filename to use
            metadata (dict): Basic metadata
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            # Save original content file first
            success, message = self.save_case_data(content, filename)
            if not success:
                return success, message
            
            # Process enhancement in background if enabled
            if self.config.context_processing_enabled:
                # Submit to thread pool for async processing
                future = self.thread_pool.submit(
                    self._process_enhanced_content, 
                    content, 
                    filename, 
                    metadata
                )
                
                # Don't wait for completion - process asynchronously
                # This prevents blocking the main thread
                self.logger.info(f"Queued enhanced processing for: {filename}")
            
            return True, f"Saved case data: {self.output_dir / filename}"
            
        except Exception as e:
            error_msg = f"Error saving enhanced case data: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def _process_enhanced_content(self, content: str, filename: str, metadata: dict):
        """Process enhanced content in background thread"""
        try:
            start_time = datetime.now()
            
            # Process content with context processor
            enhanced_result = self.context_processor.process_case_content(content, metadata)
            
            # Check if processing had errors
            if enhanced_result.get('error'):
                self.logger.warning(f"Context processing error for {filename}: {enhanced_result['error']}")
                return
            
            # Save enhanced metadata with context analysis
            enhanced_metadata_filename = filename.replace('.txt', '_enhanced_metadata.json')
            enhanced_metadata_path = self.output_dir / enhanced_metadata_filename
            
            with self.file_lock:
                temp_file = enhanced_metadata_path.with_suffix('.tmp')
                with open(temp_file, 'w', encoding=self.config.file_encoding) as f:
                    json.dump(enhanced_result, f, indent=2)
                temp_file.replace(enhanced_metadata_path)
            
            # Generate and save Support Context Protocol
            context_protocol = self.context_processor.generate_support_context_protocol(content)
            
            protocol_filename = filename.replace('.txt', '_context_protocol.json')
            protocol_path = self.output_dir / protocol_filename
            
            with self.file_lock:
                temp_file = protocol_path.with_suffix('.tmp')
                with open(temp_file, 'w', encoding=self.config.file_encoding) as f:
                    json.dump(context_protocol, f, indent=2)
                temp_file.replace(protocol_path)
            
            # Save condensed version for model consumption
            condensed_filename = filename.replace('.txt', '_condensed.txt')
            condensed_path = self.output_dir / condensed_filename
            
            condensed_content = self._generate_condensed_content(context_protocol)
            
            with self.file_lock:
                temp_file = condensed_path.with_suffix('.tmp')
                with open(temp_file, 'w', encoding=self.config.file_encoding) as f:
                    f.write(condensed_content)
                temp_file.replace(condensed_path)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            self.logger.info(f"Enhanced processing completed for {filename} in {processing_time:.2f}s")
            
        except Exception as e:
            self.logger.error(f"Error in enhanced processing for {filename}: {e}")
    
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
    
    def _generate_condensed_content(self, context_protocol: dict) -> str:
        """Generate condensed content from context protocol for model consumption
        
        Args:
            context_protocol (dict): Support Context Protocol data
            
        Returns:
            str: Condensed content optimized for model consumption
        """
        condensed = []
        
        # Header
        condensed.append("=== SUPPORT CONTEXT PROTOCOL ===")
        condensed.append(f"Generated: {context_protocol['generated_at']}")
        condensed.append("")
        
        # Case identifiers
        case_ids = context_protocol['case_identifiers']
        if case_ids['icm_id'] or case_ids['case_id']:
            condensed.append("CASE IDENTIFIERS:")
            if case_ids['icm_id']:
                condensed.append(f"  ICM ID: {case_ids['icm_id']}")
            if case_ids['case_id']:
                condensed.append(f"  Case ID: {case_ids['case_id']}")
            condensed.append("")
        
        # Priority summary
        priority = context_protocol['priority_summary']
        condensed.append("PRIORITY SUMMARY:")
        condensed.append(f"  Overall Priority: {priority['overall_priority']}")
        condensed.append(f"  Severity: {priority['severity']}")
        if priority['urgency_indicators']:
            condensed.append(f"  Urgency Indicators: {', '.join(priority['urgency_indicators'])}")
        condensed.append("")
        
        # Key facts
        key_facts = context_protocol['key_facts']
        condensed.append("KEY FACTS:")
        condensed.append(f"  Primary Issue: {key_facts['primary_issue']}")
        
        if key_facts['error_messages']:
            condensed.append("  Error Messages:")
            for error in key_facts['error_messages']:
                condensed.append(f"    - {error}")
        
        if key_facts['affected_systems']:
            condensed.append(f"  Affected Systems: {', '.join(key_facts['affected_systems'])}")
        
        customer_impact = key_facts['customer_impact']
        if customer_impact['severity'] != 'unknown':
            condensed.append(f"  Customer Impact: {customer_impact['severity']}")
        
        condensed.append("")
        
        # Context chunks (most important)
        if context_protocol['context_chunks']:
            condensed.append("IMPORTANT CONTEXT CHUNKS:")
            for i, chunk in enumerate(context_protocol['context_chunks'], 1):
                condensed.append(f"  {i}. [{chunk['type']}] [{chunk['priority']}]")
                condensed.append(f"     {chunk['summary']}")
                condensed.append("")
        
        # Actionable items
        if context_protocol['actionable_items']:
            condensed.append("ACTIONABLE ITEMS:")
            for item in context_protocol['actionable_items']:
                condensed.append(f"  - {item}")
            condensed.append("")
        
        # Tags
        if context_protocol['tags']:
            condensed.append(f"TAGS: {', '.join(context_protocol['tags'])}")
            condensed.append("")
        
        # Metadata
        metadata = context_protocol['metadata']
        condensed.append("METADATA:")
        condensed.append(f"  Original Length: {metadata['original_length']} chars")
        condensed.append(f"  Processed Chunks: {metadata['processed_chunks']}")
        condensed.append(f"  Processing Time: {metadata['processing_timestamp']}")
        
        return "\n".join(condensed)
    
    def analyze_existing_files(self) -> dict:
        """Analyze all existing .txt files in the output directory
        
        Returns:
            dict: Analysis results for all files
        """
        try:
            analysis_results = {
                'total_files': 0,
                'processed_files': 0,
                'failed_files': 0,
                'files': [],
                'summary': {
                    'content_types': {},
                    'priority_levels': {},
                    'tags': {},
                    'average_length': 0
                }
            }
            
            case_files = self.list_case_files()
            analysis_results['total_files'] = len(case_files)
            
            total_length = 0
            
            for file_path in case_files:
                try:
                    # Read file content
                    with open(file_path, 'r', encoding=self.config.file_encoding) as f:
                        content = f.read()
                    
                    # Skip if already has enhanced processing
                    enhanced_file = file_path.with_name(file_path.stem + '_enhanced_metadata.json')
                    if enhanced_file.exists():
                        analysis_results['processed_files'] += 1
                        continue
                    
                    # Generate context protocol for existing file
                    context_protocol = self.context_processor.generate_support_context_protocol(content)
                    
                    # Save enhanced analysis
                    enhanced_filename = file_path.stem + '_enhanced_metadata.json'
                    enhanced_path = self.output_dir / enhanced_filename
                    
                    with open(enhanced_path, 'w', encoding=self.config.file_encoding) as f:
                        json.dump(context_protocol, f, indent=2)
                    
                    # Save condensed version
                    condensed_filename = file_path.stem + '_condensed.txt'
                    condensed_path = self.output_dir / condensed_filename
                    
                    condensed_content = self._generate_condensed_content(context_protocol)
                    
                    with open(condensed_path, 'w', encoding=self.config.file_encoding) as f:
                        f.write(condensed_content)
                    
                    # Add to analysis results
                    file_analysis = {
                        'filename': file_path.name,
                        'original_length': len(content),
                        'priority': context_protocol['priority_summary']['overall_priority'],
                        'severity': context_protocol['priority_summary']['severity'],
                        'tags': context_protocol['tags'],
                        'primary_issue': context_protocol['key_facts']['primary_issue']
                    }
                    
                    analysis_results['files'].append(file_analysis)
                    analysis_results['processed_files'] += 1
                    
                    # Update summary statistics
                    total_length += len(content)
                    
                    # Count content types, priorities, and tags
                    for chunk in context_protocol.get('context_chunks', []):
                        content_type = chunk['type']
                        analysis_results['summary']['content_types'][content_type] = \
                            analysis_results['summary']['content_types'].get(content_type, 0) + 1
                        
                        priority = chunk['priority']
                        analysis_results['summary']['priority_levels'][priority] = \
                            analysis_results['summary']['priority_levels'].get(priority, 0) + 1
                    
                    for tag in context_protocol['tags']:
                        analysis_results['summary']['tags'][tag] = \
                            analysis_results['summary']['tags'].get(tag, 0) + 1
                    
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")
                    analysis_results['failed_files'] += 1
            
            # Calculate average length
            if analysis_results['processed_files'] > 0:
                analysis_results['summary']['average_length'] = total_length / analysis_results['processed_files']
            
            return analysis_results
            
        except Exception as e:
            print(f"Error analyzing existing files: {e}")
            return {
                'total_files': 0,
                'processed_files': 0,
                'failed_files': 0,
                'files': [],
                'summary': {},
                'error': str(e)
            }
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if hasattr(self, 'thread_pool'):
                self.thread_pool.shutdown(wait=False)
                self.logger.info("Thread pool shutdown completed")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()
