"""
Context processor for enhancing case data with LangChain chunking and analysis
"""
import json
import re
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from functools import lru_cache

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_core.documents import Document
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("LangChain not available - install langchain for enhanced context processing")

try:
    from .config import Config
    from .data_parser import DataParser
    from .logger import get_logger
except ImportError:
    from config import Config
    from data_parser import DataParser
    from logger import get_logger


class ContextProcessor:
    """Enhanced context processor using LangChain for better document analysis"""
    
    def __init__(self, config: Config):
        """Initialize context processor
        
        Args:
            config (Config): Application configuration
        """
        self.config = config
        self.data_parser = DataParser()
        self.logger = get_logger(config)
        
        # Initialize LangChain text splitter if available
        if LANGCHAIN_AVAILABLE:
            chunk_size = 1000 if config.performance_mode else 500
            chunk_overlap = 200 if config.performance_mode else 100
            
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", ".", "!", "?", ";", ":", " ", ""]
            )
        else:
            self.text_splitter = None
        
        # Thread pool for parallel processing
        self.thread_pool = ThreadPoolExecutor(max_workers=2)
        
        # Compile regex patterns for better performance
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for better performance"""
        self.patterns = {
            'error_patterns': [
                re.compile(r'error[:\s]+([^\n]+)', re.IGNORECASE),
                re.compile(r'exception[:\s]+([^\n]+)', re.IGNORECASE),
                re.compile(r'failed[:\s]+([^\n]+)', re.IGNORECASE),
                re.compile(r'unable to[:\s]+([^\n]+)', re.IGNORECASE)
            ],
            'timestamp_patterns': [
                re.compile(r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}'),
                re.compile(r'\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}'),
                re.compile(r'\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2}')
            ],
            'entity_patterns': {
                'ip_address': re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
                'url': re.compile(r'https?://[^\s<>"]+'),
                'file_path': re.compile(r'[A-Za-z]:\\[^\s<>"]+'),
                'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
                'server_name': re.compile(r'\b[A-Za-z0-9-]+\.[A-Za-z0-9.-]+\b'),
                'guid': re.compile(r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b')
            },
            'priority_keywords': {
                'high': ['critical', 'urgent', 'emergency', 'outage', 'down', 'failed'],
                'medium': ['important', 'significant', 'major', 'escalation'],
                'low': ['minor', 'cosmetic', 'enhancement', 'suggestion']
            }
        }
    
    def process_case_content(self, content: str, metadata: Dict) -> Dict:
        """Process case content with enhanced context analysis
        
        Args:
            content (str): Raw case content
            metadata (Dict): Basic metadata from data_parser
            
        Returns:
            Dict: Enhanced processing result with chunked content and analysis
        """
        start_time = time.time()
        result = {
            'original_content': content,
            'metadata': metadata,
            'chunks': [],
            'context_summary': {},
            'tags': [],
            'key_information': {},
            'processed_at': datetime.now().isoformat(),
            'processing_time': 0,
            'error': None
        }
        
        try:
            if not LANGCHAIN_AVAILABLE:
                result['error'] = "LangChain not available for enhanced processing"
                return result
            
            # Run with timeout to prevent hanging
            future = self.thread_pool.submit(self._process_with_timeout, content, metadata)
            
            try:
                processed_result = future.result(timeout=self.config.context_processing_timeout)
                result.update(processed_result)
            except TimeoutError:
                self.logger.warning(f"Context processing timed out after {self.config.context_processing_timeout}s")
                result['error'] = "Processing timed out"
                return result
            
        except Exception as e:
            self.logger.error(f"Error in context processing: {e}")
            result['error'] = str(e)
        finally:
            result['processing_time'] = time.time() - start_time
            
        return result
    
    def _process_with_timeout(self, content: str, metadata: Dict) -> Dict:
        """Process content with timeout protection"""
        result = {
            'chunks': [],
            'context_summary': {},
            'tags': [],
            'key_information': {}
        }
        
        # Create chunks using LangChain
        documents = [Document(page_content=content, metadata=metadata)]
        chunks = self.text_splitter.split_documents(documents)
        
        # Process chunks in parallel if performance mode is enabled
        if self.config.performance_mode and len(chunks) > 1:
            # Parallel processing for large content
            chunk_futures = []
            for i, chunk in enumerate(chunks):
                future = self.thread_pool.submit(self._analyze_chunk, chunk.page_content, i)
                chunk_futures.append((i, chunk, future))
            
            for i, chunk, future in chunk_futures:
                try:
                    chunk_analysis = future.result(timeout=5)  # 5 second timeout per chunk
                    result['chunks'].append({
                        'chunk_id': i,
                        'content': chunk.page_content,
                        'analysis': chunk_analysis,
                        'metadata': chunk.metadata
                    })
                except TimeoutError:
                    self.logger.warning(f"Chunk {i} analysis timed out")
                    continue
        else:
            # Sequential processing for smaller content
            for i, chunk in enumerate(chunks):
                chunk_analysis = self._analyze_chunk(chunk.page_content, i)
                result['chunks'].append({
                    'chunk_id': i,
                    'content': chunk.page_content,
                    'analysis': chunk_analysis,
                    'metadata': chunk.metadata
                })
        
        # Generate overall context summary
        result['context_summary'] = self._generate_context_summary(content, chunks)
        
        # Extract key information and tags
        result['key_information'] = self._extract_key_information(content)
        result['tags'] = self._generate_tags(content, result['key_information'])
        
        return result
    
    def _analyze_chunk(self, chunk_content: str, chunk_id: int) -> Dict:
        """Analyze individual chunk for specific patterns and context
        
        Args:
            chunk_content (str): Content of the chunk
            chunk_id (int): Unique identifier for the chunk
            
        Returns:
            Dict: Analysis results for the chunk
        """
        analysis = {
            'chunk_id': chunk_id,
            'length': len(chunk_content),
            'word_count': len(chunk_content.split()),
            'line_count': len(chunk_content.splitlines()),
            'contains_case_ids': False,
            'content_type': 'general',
            'priority_level': 'normal',
            'key_phrases': [],
            'entities': []
        }
        
        # Check for case IDs in this chunk
        ids = self.data_parser.extract_case_ids(chunk_content)
        analysis['contains_case_ids'] = any(ids.values())
        analysis['extracted_ids'] = ids
        
        # Determine content type based on patterns
        analysis['content_type'] = self._classify_content_type(chunk_content)
        
        # Determine priority level
        analysis['priority_level'] = self._determine_priority_level(chunk_content)
        
        # Extract key phrases and entities
        analysis['key_phrases'] = self._extract_key_phrases(chunk_content)
        analysis['entities'] = self._extract_entities(chunk_content)
        
        return analysis
    
    def _classify_content_type(self, content: str) -> str:
        """Classify the type of content in the chunk
        
        Args:
            content (str): Content to classify
            
        Returns:
            str: Content type classification
        """
        content_lower = content.lower()
        
        # Priority order for classification
        if any(keyword in content_lower for keyword in ['error', 'exception', 'failed', 'failure']):
            return 'error_information'
        elif any(keyword in content_lower for keyword in ['critical', 'urgent', 'emergency']):
            return 'critical_information'
        elif any(keyword in content_lower for keyword in ['resolution', 'solution', 'fix', 'resolved']):
            return 'resolution_information'
        elif any(keyword in content_lower for keyword in ['symptom', 'issue', 'problem']):
            return 'problem_description'
        elif any(keyword in content_lower for keyword in ['customer', 'client', 'user']):
            return 'customer_information'
        elif any(keyword in content_lower for keyword in ['timeline', 'schedule', 'date', 'time']):
            return 'temporal_information'
        elif any(keyword in content_lower for keyword in ['configuration', 'settings', 'setup']):
            return 'configuration_information'
        else:
            return 'general_information'
    
    @lru_cache(maxsize=128)
    def _determine_priority_level(self, content: str) -> str:
        """Determine priority level of content (cached for performance)
        
        Args:
            content (str): Content to analyze
            
        Returns:
            str: Priority level (high, medium, normal, low)
        """
        content_lower = content.lower()
        
        # Check priority levels in order
        for priority, keywords in self.patterns['priority_keywords'].items():
            if any(keyword in content_lower for keyword in keywords):
                return priority
        
        return 'normal'
    
    def _extract_key_phrases(self, content: str) -> List[str]:
        """Extract key phrases from content
        
        Args:
            content (str): Content to analyze
            
        Returns:
            List[str]: List of key phrases
        """
        key_phrases = []
        
        # Common support case patterns
        patterns = [
            r'error\s+\w+',
            r'exception\s+\w+',
            r'failed\s+to\s+\w+',
            r'unable\s+to\s+\w+',
            r'timeout\s+\w+',
            r'connection\s+\w+',
            r'authentication\s+\w+',
            r'authorization\s+\w+',
            r'performance\s+\w+',
            r'latency\s+\w+',
            r'memory\s+\w+',
            r'cpu\s+\w+',
            r'disk\s+\w+',
            r'network\s+\w+'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            key_phrases.extend(matches)
        
        return list(set(key_phrases))  # Remove duplicates
    
    def _extract_entities(self, content: str) -> List[Dict]:
        """Extract entities like IPs, URLs, file paths, etc. (optimized)
        
        Args:
            content (str): Content to analyze
            
        Returns:
            List[Dict]: List of extracted entities
        """
        entities = []
        
        # Use compiled patterns for better performance
        for entity_type, pattern in self.patterns['entity_patterns'].items():
            matches = pattern.findall(content)
            for match in matches:
                entities.append({
                    'type': entity_type,
                    'value': match,
                    'context': self._get_entity_context(content, match)
                })
        
        return entities
    
    def _get_entity_context(self, content: str, entity: str) -> str:
        """Get context around an entity
        
        Args:
            content (str): Full content
            entity (str): Entity to find context for
            
        Returns:
            str: Context around the entity
        """
        entity_index = content.find(entity)
        if entity_index == -1:
            return ""
        
        # Get 100 characters before and after
        start = max(0, entity_index - 100)
        end = min(len(content), entity_index + len(entity) + 100)
        
        return content[start:end].strip()
    
    def _generate_context_summary(self, content: str, chunks: List) -> Dict:
        """Generate overall context summary
        
        Args:
            content (str): Original content
            chunks (List): Processed chunks
            
        Returns:
            Dict: Context summary
        """
        summary = {
            'total_chunks': len(chunks),
            'total_length': len(content),
            'content_types': {},
            'priority_distribution': {},
            'key_topics': []
        }
        
        # Analyze chunk distribution
        for chunk in chunks:
            chunk_analysis = self._analyze_chunk(chunk.page_content, 0)
            
            # Count content types
            content_type = chunk_analysis['content_type']
            summary['content_types'][content_type] = summary['content_types'].get(content_type, 0) + 1
            
            # Count priority levels
            priority = chunk_analysis['priority_level']
            summary['priority_distribution'][priority] = summary['priority_distribution'].get(priority, 0) + 1
        
        # Extract key topics (most common content types)
        summary['key_topics'] = sorted(
            summary['content_types'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return summary
    
    def _extract_key_information(self, content: str) -> Dict:
        """Extract key information for efficient context passing
        
        Args:
            content (str): Content to analyze
            
        Returns:
            Dict: Key information extracted
        """
        key_info = {
            'case_identifiers': self.data_parser.extract_case_ids(content),
            'error_messages': self._extract_error_messages(content),
            'timestamps': self._extract_timestamps(content),
            'system_information': self._extract_system_info(content),
            'customer_impact': self._extract_customer_impact(content),
            'resolution_steps': self._extract_resolution_steps(content)
        }
        
        return key_info
    
    def _extract_error_messages(self, content: str) -> List[str]:
        """Extract error messages from content (optimized)"""
        errors = []
        
        # Use compiled patterns for better performance
        for pattern in self.patterns['error_patterns']:
            matches = pattern.findall(content)
            errors.extend(matches)
        
        return list(set(errors))
    
    def _extract_timestamps(self, content: str) -> List[str]:
        """Extract timestamps from content (optimized)"""
        timestamps = []
        
        # Use compiled patterns for better performance
        for pattern in self.patterns['timestamp_patterns']:
            matches = pattern.findall(content)
            timestamps.extend(matches)
        
        return list(set(timestamps))
    
    def _extract_system_info(self, content: str) -> Dict:
        """Extract system information from content"""
        system_info = {
            'operating_system': [],
            'applications': [],
            'versions': [],
            'hardware': []
        }
        
        # OS patterns
        os_patterns = [
            r'windows\s+\d+',
            r'linux\s+\w+',
            r'ubuntu\s+\d+',
            r'centos\s+\d+',
            r'red\s+hat\s+\d+'
        ]
        
        for pattern in os_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            system_info['operating_system'].extend(matches)
        
        # Version patterns
        version_patterns = [
            r'version\s+\d+\.\d+\.\d+',
            r'v\d+\.\d+\.\d+',
            r'build\s+\d+'
        ]
        
        for pattern in version_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            system_info['versions'].extend(matches)
        
        return system_info
    
    def _extract_customer_impact(self, content: str) -> Dict:
        """Extract customer impact information"""
        impact_info = {
            'severity': 'unknown',
            'affected_users': [],
            'business_impact': []
        }
        
        content_lower = content.lower()
        
        # Determine severity
        if any(keyword in content_lower for keyword in ['critical', 'sev1', 'severity 1']):
            impact_info['severity'] = 'critical'
        elif any(keyword in content_lower for keyword in ['high', 'sev2', 'severity 2']):
            impact_info['severity'] = 'high'
        elif any(keyword in content_lower for keyword in ['medium', 'sev3', 'severity 3']):
            impact_info['severity'] = 'medium'
        elif any(keyword in content_lower for keyword in ['low', 'sev4', 'severity 4']):
            impact_info['severity'] = 'low'
        
        # Extract user impact
        user_patterns = [
            r'(\d+)\s+users?\s+affected',
            r'affecting\s+(\d+)\s+users?',
            r'(\d+)\s+customers?\s+impacted'
        ]
        
        for pattern in user_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            impact_info['affected_users'].extend(matches)
        
        return impact_info
    
    def _extract_resolution_steps(self, content: str) -> List[str]:
        """Extract resolution steps from content"""
        resolution_patterns = [
            r'resolution[:\s]+([^\n]+)',
            r'solution[:\s]+([^\n]+)',
            r'fix[:\s]+([^\n]+)',
            r'workaround[:\s]+([^\n]+)'
        ]
        
        steps = []
        for pattern in resolution_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            steps.extend(matches)
        
        return list(set(steps))
    
    def _generate_tags(self, content: str, key_info: Dict) -> List[str]:
        """Generate tags for the content
        
        Args:
            content (str): Content to tag
            key_info (Dict): Key information extracted
            
        Returns:
            List[str]: List of tags
        """
        tags = []
        
        # Add case ID tags
        if key_info['case_identifiers']['icm_id']:
            tags.append(f"ICM-{key_info['case_identifiers']['icm_id']}")
        if key_info['case_identifiers']['case_id']:
            tags.append(f"Case-{key_info['case_identifiers']['case_id']}")
        
        # Add severity tags
        if key_info['customer_impact']['severity'] != 'unknown':
            tags.append(f"severity-{key_info['customer_impact']['severity']}")
        
        # Add content type tags
        content_lower = content.lower()
        if 'error' in content_lower:
            tags.append('error')
        if 'resolution' in content_lower:
            tags.append('resolution')
        if 'customer' in content_lower:
            tags.append('customer-facing')
        if 'internal' in content_lower:
            tags.append('internal')
        
        return list(set(tags))
    
    def generate_support_context_protocol(self, content: str) -> Dict:
        """Generate Support Context Protocol - condensed version for model consumption
        
        Args:
            content (str): Original content
            
        Returns:
            Dict: Support Context Protocol data
        """
        # Process the content first
        metadata = self.data_parser.extract_metadata(content)
        processed_result = self.process_case_content(content, metadata)
        
        # Create condensed protocol
        protocol = {
            'protocol_version': '1.0',
            'generated_at': datetime.now().isoformat(),
            'case_identifiers': processed_result['key_information']['case_identifiers'],
            'priority_summary': {
                'overall_priority': self._determine_priority_level(content),
                'severity': processed_result['key_information']['customer_impact']['severity'],
                'urgency_indicators': self._extract_urgency_indicators(content)
            },
            'key_facts': {
                'primary_issue': self._extract_primary_issue(content),
                'error_messages': processed_result['key_information']['error_messages'][:3],  # Top 3
                'affected_systems': self._extract_affected_systems(content),
                'customer_impact': processed_result['key_information']['customer_impact']
            },
            'context_chunks': [
                {
                    'type': chunk['analysis']['content_type'],
                    'priority': chunk['analysis']['priority_level'],
                    'summary': chunk['content'][:200] + '...' if len(chunk['content']) > 200 else chunk['content']
                }
                for chunk in processed_result['chunks']
                if chunk['analysis']['priority_level'] in ['high', 'medium']
            ][:5],  # Top 5 most important chunks
            'actionable_items': self._extract_actionable_items(content),
            'tags': processed_result['tags'],
            'metadata': {
                'original_length': len(content),
                'processed_chunks': len(processed_result['chunks']),
                'processing_timestamp': processed_result['processed_at']
            }
        }
        
        return protocol
    
    def _extract_urgency_indicators(self, content: str) -> List[str]:
        """Extract urgency indicators from content"""
        urgency_patterns = [
            r'urgent',
            r'asap',
            r'immediate',
            r'emergency',
            r'critical',
            r'outage',
            r'down',
            r'not working'
        ]
        
        indicators = []
        content_lower = content.lower()
        
        for pattern in urgency_patterns:
            if pattern in content_lower:
                indicators.append(pattern)
        
        return indicators
    
    def _extract_primary_issue(self, content: str) -> str:
        """Extract the primary issue from content"""
        # Look for common issue patterns
        issue_patterns = [
            r'issue[:\s]+([^\n]+)',
            r'problem[:\s]+([^\n]+)',
            r'error[:\s]+([^\n]+)',
            r'unable to[:\s]+([^\n]+)'
        ]
        
        for pattern in issue_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # If no specific pattern found, return first line that looks like an issue
        lines = content.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['issue', 'problem', 'error', 'unable']):
                return line.strip()
        
        return "Primary issue not clearly identified"
    
    def _extract_affected_systems(self, content: str) -> List[str]:
        """Extract affected systems from content"""
        system_patterns = [
            r'server[:\s]+([^\s\n]+)',
            r'application[:\s]+([^\s\n]+)',
            r'service[:\s]+([^\s\n]+)',
            r'database[:\s]+([^\s\n]+)',
            r'system[:\s]+([^\s\n]+)'
        ]
        
        systems = []
        for pattern in system_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            systems.extend(matches)
        
        return list(set(systems))
    
    def _extract_actionable_items(self, content: str) -> List[str]:
        """Extract actionable items from content"""
        action_patterns = [
            r'action[:\s]+([^\n]+)',
            r'todo[:\s]+([^\n]+)',
            r'next step[:\s]+([^\n]+)',
            r'follow up[:\s]+([^\n]+)',
            r'escalate[:\s]+([^\n]+)'
        ]
        
        actions = []
        for pattern in action_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            actions.extend(matches)
        
        return list(set(actions))