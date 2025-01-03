from typing import List, Dict, Optional
import os
from flask import current_app

class PromptTemplate:
    """Prompt templates for file assistant"""
    
    FILE_MATCHING = """You are a file assistant helping users find, open, and close files.

Available files in {base_dir}:
{files}

File type categories:
- Documents: {document_types}
- Images: {image_types}
- Data files: {data_types}

Instructions:
1. Match files based on the user's description
2. Support natural language queries in any language
3. When user mentions:
   - "document" -> match any document type
   - "image" -> match any image type
   - "data" -> match any data file type
4. For file operations, return in the following format:
   - When user wants to "open" or "打开": operation: open, filename: <the filename>
   - When user wants to "close" or "关闭" or "关上": operation: close, filename: <the filename>
   - For both operations, you should use the same file matching logic to find the correct file
5. If no files match, return "No matching files found."

User query: {query}

Response:"""
class PromptService:
    def __init__(self):
        self.templates = {
            'file_matching': PromptTemplate.FILE_MATCHING
        }
        self.current_template = 'file_matching'
    
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
    
    def combine_prompt(self, user_query, files):
        """Combine user query and file list into a prompt"""
        base_dir, files_str = self.format_file_list(files)
        file_types = self.get_file_types()
        print("==========file_types==========")
        print(file_types)
        print("==========file_types==========")
        
        return self.templates[self.current_template].format(
            query=user_query,
            base_dir=base_dir,
            files=files_str,
            **file_types
        )