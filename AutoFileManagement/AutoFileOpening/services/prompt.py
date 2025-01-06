from typing import List, Dict, Optional
import os
from flask import current_app
from models.prompts.file_assistant import FileAssistantPrompt

class PromptService:
    def __init__(self):
        self.templates = {
            'operation': FileAssistantPrompt.OPERATION_DETECTION,
            'file_matching': FileAssistantPrompt.FILE_MATCHING
        }
    
    def format_file_list(self, files):
        """Format file list in a concise way"""
        # Get base directory from the first file
        if not files:
            return "", ""
            
        base_dir = os.path.dirname(files[0]['path']) if 'path' in files[0] else ""
        
        # Just list file names
        file_list = []
        for file in files:
            if 'path' in file:
                name = os.path.basename(file['path'])
                ext = os.path.splitext(name)[1][1:] or 'unknown'
                file_list.append(f"- {name} ({ext})")
        
        return base_dir, '\n'.join(file_list)
    
    def get_file_types(self):
        """Get file type categories from config"""
        file_types = current_app.config.get('AUTO_FILE_OPENING_FILE_TYPES', {})
        return {
            'document_types': ', '.join(file_types.get('DOCUMENT', [])),
            'image_types': ', '.join(file_types.get('IMAGE', [])),
            'data_types': ', '.join(file_types.get('DATA', [])),
            'archieve': ', '.join(file_types.get('ARCHIVES', []))
        }
        
    def get_operation_prompt(self, user_query):
        """Get operation detection prompt"""
        return self.templates['operation'].format(query=user_query)
        
    def get_file_matching_prompt(self, user_query, files):
        """Get file matching prompt"""
        base_dir, files_str = self.format_file_list(files)
        file_types = self.get_file_types()
        
        return self.templates['file_matching'].format(
            query=user_query,
            base_dir=base_dir,
            files=files_str,
            **file_types
        )