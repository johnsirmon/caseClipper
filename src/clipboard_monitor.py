"""
Clipboard monitoring functionality
"""
import time
import threading
from typing import Optional, Callable
from datetime import datetime
import pyperclip

try:
    from .data_parser import DataParser
    from .file_manager import FileManager
    from .config import Config
    from .logger import get_logger
except ImportError:
    from data_parser import DataParser
    from file_manager import FileManager
    from config import Config
    from logger import get_logger


class ClipboardMonitor:
    """Monitors clipboard for case review data"""
    
    def __init__(self, config: Config, file_manager: FileManager, 
                 on_data_processed: Optional[Callable] = None):
        """Initialize clipboard monitor
        
        Args:
            config (Config): Application configuration
            file_manager (FileManager): File manager instance
            on_data_processed (Callable, optional): Callback for processed data
        """
        self.config = config
        self.file_manager = file_manager
        self.data_parser = DataParser()
        self.on_data_processed = on_data_processed
        self.logger = get_logger(config)
        
        self.monitoring = False
        self.monitor_thread = None
        self.last_content = ""
        self.last_check_time = datetime.now()
        
        # Performance optimizations
        self.max_content_length = config.max_file_size_mb * 1024 * 1024 if config else 10 * 1024 * 1024
        self.content_hash_cache = set()  # Cache for detecting duplicates
    
    def start_monitoring(self) -> bool:
        """Start clipboard monitoring
        
        Returns:
            bool: True if monitoring started successfully
        """
        if self.monitoring:
            return True
        
        try:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            self.logger.info("Clipboard monitoring started")
            return True
        except Exception as e:
            self.logger.error(f"Error starting clipboard monitoring: {e}")
            self.monitoring = False
            return False
    
    def stop_monitoring(self):
        """Stop clipboard monitoring"""
        if not self.monitoring:
            return
        
        self.monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2.0)
        
        self.logger.info("Clipboard monitoring stopped")
    
    def is_monitoring(self) -> bool:
        """Check if monitoring is active
        
        Returns:
            bool: True if monitoring is active
        """
        return self.monitoring
    
    def _monitor_loop(self):
        """Main monitoring loop (runs in separate thread)"""
        while self.monitoring:
            try:
                current_content = self._get_clipboard_content()
                
                if current_content and current_content != self.last_content:
                    # Check content length limit
                    if len(current_content) > self.max_content_length:
                        self.logger.warning(f"Content too large ({len(current_content)} bytes), skipping")
                        continue
                    
                    # Check for duplicate content using hash
                    content_hash = hash(current_content)
                    if content_hash not in self.content_hash_cache:
                        self.content_hash_cache.add(content_hash)
                        self._process_clipboard_content(current_content)
                        
                        # Limit cache size
                        if len(self.content_hash_cache) > 100:
                            self.content_hash_cache.clear()
                    
                    self.last_content = current_content
                
                self.last_check_time = datetime.now()
                time.sleep(self.config.polling_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.config.polling_interval)
    
    def _get_clipboard_content(self) -> Optional[str]:
        """Get current clipboard content
        
        Returns:
            Optional[str]: Clipboard content or None if error
        """
        try:
            content = pyperclip.paste()
            return content if content else None
        except Exception as e:
            self.logger.error(f"Error accessing clipboard: {e}")
            return None
    
    def _process_clipboard_content(self, content: str):
        """Process clipboard content for case data
        
        Args:
            content (str): Clipboard content to process
        """
        try:
            self.logger.debug(f"Processing clipboard content (length: {len(content)})")
            
            # Check if content contains valid case data
            if not self.data_parser.is_valid_case_data(content):
                self.logger.debug("No valid case data found in clipboard")
                return
            
            self.logger.info("Valid case data detected!")
            
            # Extract IDs and generate filename
            filename = self.data_parser.generate_filename(content)
            if not filename:
                self.logger.warning("Could not generate filename from clipboard content")
                return
            
            self.logger.info(f"Generated filename: {filename}")
            
            # Get metadata
            metadata = self.data_parser.extract_metadata(content)
            
            # Save the file with enhanced processing (if enabled)
            if self.config.context_processing_enabled:
                success, message = self.file_manager.save_enhanced_case_data(
                    content, filename, metadata
                )
            else:
                success, message = self.file_manager.save_with_metadata(
                    content, filename, metadata
                )
            
            self.logger.info(f"Save result: success={success}, message={message}")
            
            # Prepare result data
            result_data = {
                'success': success,
                'message': message,
                'filename': filename,
                'content': content,
                'metadata': metadata,
                'timestamp': datetime.now().isoformat()
            }
            
            # Call callback if provided
            if self.on_data_processed:
                self.on_data_processed(result_data)
            
            if success:
                self.logger.info(f"✓ Case data saved: {filename}")
            else:
                self.logger.error(f"✗ Failed to save case data: {message}")
                
        except Exception as e:
            error_msg = f"Error processing clipboard content: {e}"
            self.logger.exception(error_msg)
            
            if self.on_data_processed:
                self.on_data_processed({
                    'success': False,
                    'message': error_msg,
                    'filename': None,
                    'content': content,
                    'metadata': {},
                    'timestamp': datetime.now().isoformat()
                })
    
    def test_current_clipboard(self) -> dict:
        """Test current clipboard content (for debugging)
        
        Returns:
            dict: Test results
        """
        content = self._get_clipboard_content()
        
        if not content:
            return {
                'has_content': False,
                'is_valid_case_data': False,
                'message': 'No clipboard content'
            }
        
        is_valid = self.data_parser.is_valid_case_data(content)
        ids = self.data_parser.extract_case_ids(content)
        filename = self.data_parser.generate_filename(content) if is_valid else None
        
        return {
            'has_content': True,
            'content_length': len(content),
            'is_valid_case_data': is_valid,
            'extracted_ids': ids,
            'generated_filename': filename,
            'preview': content[:200] + '...' if len(content) > 200 else content,
            'message': 'Valid case data found' if is_valid else 'No valid case data found'
        }
    
    def get_status(self) -> dict:
        """Get monitoring status
        
        Returns:
            dict: Status information
        """
        return {
            'monitoring': self.monitoring,
            'last_check': self.last_check_time.isoformat(),
            'polling_interval': self.config.polling_interval,
            'output_directory': self.config.output_directory,
            'thread_alive': self.monitor_thread.is_alive() if self.monitor_thread else False
        }
