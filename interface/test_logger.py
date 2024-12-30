import os
import json
from datetime import datetime
import time
from flask import current_app

class TestLogger:
    """Test logger for debugging and analysis"""
    
    def __init__(self):
        # Load test logging configuration
        self.enabled = {
            'prompt': current_app.config.get('TEST_PROMPT_LOGGING', True),
            'llm_response': current_app.config.get('TEST_LLM_RESPONSE_LOGGING', True),
            'file_info': current_app.config.get('TEST_FILE_INFO_LOGGING', True),
            'directory_info': current_app.config.get('TEST_DIRECTORY_INFO_LOGGING', True),
            'local_state': current_app.config.get('TEST_LOCAL_STATE_LOGGING', True)
        }
        
        # Use LOG_DIR from environment or config
        log_dir = os.getenv('LOG_DIR', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs'))
        self.log_file = os.path.join(log_dir, 'test_log.jsonl')
        self.log_format = current_app.config.get('TEST_LOG_FORMAT', 'jsonl')
        self.execution_start = None
        
        # Create logs directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
    
    def start_execution(self, title=None):
        """Start a new test execution"""
        self.execution_start = time.time()
        separator = "=" * 50
        title = title or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = f"\n{separator}\n{title}\n{separator}\n"
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(header)
    
    def end_execution(self):
        """End current test execution"""
        if self.execution_start:
            runtime = time.time() - self.execution_start
            footer = f"\nExecution completed in {runtime:.2f} seconds\n\n"
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(footer)
            self.execution_start = None
    
    def _format_content(self, content):
        """Format content with proper line breaks"""
        if isinstance(content, str):
            # Preserve existing line breaks and add breaks at reasonable points
            formatted = content.replace('\\n', '\n')
            # Add breaks after punctuation marks if line is too long
            lines = []
            current_line = ""
            for word in formatted.split():
                if len(current_line) + len(word) > 80:  # 80 chars per line
                    lines.append(current_line)
                    current_line = word
                else:
                    current_line = f"{current_line} {word}" if current_line else word
                if any(word.endswith(p) for p in ['.', '?', '!', ';', ':']):
                    lines.append(current_line)
                    current_line = ""
            if current_line:
                lines.append(current_line)
            return '\n'.join(lines)
        return content
    
    def _write_log(self, data):
        """Write log entry to file"""
        try:
            # Add timestamp
            data['timestamp'] = datetime.now().isoformat()
            
            # Format content with proper line breaks
            if isinstance(data.get('content'), dict):
                for key, value in data['content'].items():
                    if isinstance(value, str):
                        data['content'][key] = self._format_content(value)
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                if self.log_format == 'jsonl':
                    # Format JSON with proper indentation and line breaks
                    formatted_json = json.dumps(data, ensure_ascii=False, indent=2)
                    f.write(formatted_json + '\n')
                else:
                    # For plain format, preserve formatting
                    content = json.dumps(data['content'], ensure_ascii=False, indent=2)
                    f.write(f"[{data['timestamp']}] {data['type']}:\n{content}\n")
        except Exception as e:
            current_app.logger.error(f"Error writing test log: {str(e)}")
    
    def log_prompt(self, prompt, context=None):
        """Log prompt information"""
        if not self.enabled['prompt']:
            return
            
        self._write_log({
            'type': 'prompt',
            'content': {
                'prompt': prompt,
                'context': context
            }
        })
    
    def log_llm_response(self, response, metadata=None):
        """Log LLM response"""
        if not self.enabled['llm_response']:
            return
            
        self._write_log({
            'type': 'llm_response',
            'content': {
                'response': response,
                'metadata': metadata
            }
        })
    
    def log_file_info(self, file_info):
        """Log file information"""
        if not self.enabled['file_info']:
            return
            
        self._write_log({
            'type': 'file_info',
            'content': file_info
        })
    
    def log_directory_info(self, directory_info):
        """Log directory information"""
        if not self.enabled['directory_info']:
            return
            
        self._write_log({
            'type': 'directory_info',
            'content': directory_info
        })
    
    def log_local_state(self, state_info):
        """Log local state information"""
        if not self.enabled['local_state']:
            return
            
        self._write_log({
            'type': 'local_state',
            'content': state_info
        })
    
    def get_logs(self, log_types=None, start_time=None, end_time=None):
        """
        Get filtered logs
        
        Args:
            log_types (list, optional): Types of logs to retrieve
            start_time (datetime, optional): Start time filter
            end_time (datetime, optional): End time filter
            
        Returns:
            list: Filtered log entries
        """
        try:
            logs = []
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        
                        # Apply filters
                        if log_types and entry['type'] not in log_types:
                            continue
                            
                        if start_time and datetime.fromisoformat(entry['timestamp']) < start_time:
                            continue
                            
                        if end_time and datetime.fromisoformat(entry['timestamp']) > end_time:
                            continue
                        
                        logs.append(entry)
                    except json.JSONDecodeError:
                        continue
                        
            return logs
        except FileNotFoundError:
            return []
        except Exception as e:
            current_app.logger.error(f"Error reading test logs: {str(e)}")
            return [] 