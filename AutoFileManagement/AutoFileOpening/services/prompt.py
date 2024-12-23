from typing import List, Dict, Optional

class PromptTemplate:
    """Base templates for different types of prompts"""
    
    FILE_ASSISTANT = """
    You are a file assistant. Your job is to process user queries to locate files on their local computer. 
    The user will provide a natural language query, and you must return the exact file path based on the following rules:

    1. Understand the user's intent (e.g., file name, file type, location).
    2. Match the file query with the available files from the provided directory list.
    3. If the user requests the "latest" file, select the most recently modified file of the specified type.
    4. If multiple files match, return a list of possible file paths for clarification.
    5. If no files match, respond with "No matching files found."

    Directory structure:
    {directory_list}

    Examples:
    User query: "Please open the file named 'LLM.pptx'."
    Response: "/Users/username/Desktop/LLM.pptx"

    Now process the following query:
    User query: "{user_query}"
    Response:
    """

    FILE_ANALYZER = """
    You are a file analyzer. Your job is to understand file patterns and suggest relevant files based on user needs.
    Available files:
    {directory_list}

    User query: "{user_query}"
    Analyze and suggest relevant files based on:
    1. Content relevance
    2. File type appropriateness
    3. Recent modifications
    """

class PromptService:
    def __init__(self):
        self.templates = {
            'file_assistant': PromptTemplate.FILE_ASSISTANT,
            'file_analyzer': PromptTemplate.FILE_ANALYZER
        }
        self.current_template = 'file_assistant'
        self.custom_prompts = []

    def set_template(self, template_name: str) -> None:
        """
        Set the current prompt template
        
        Args:
            template_name (str): Name of the template to use
        """
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")
        self.current_template = template_name

    def add_template(self, name: str, template: str) -> None:
        """
        Add a new prompt template
        
        Args:
            name (str): Name of the new template
            template (str): The template string
        """
        self.templates[name] = template

    def format_directory_list(self, files: List[Dict]) -> str:
        """
        Format file list for prompt
        
        Args:
            files (List[Dict]): List of file information dictionaries
            
        Returns:
            str: Formatted directory listing
        """
        formatted_list = []
        for file in files:
            formatted_list.append(
                f"- {file['name']} ({file['type']}) in {file['directory']}"
            )
        return "\n".join(formatted_list)

    def combine_prompt(self, 
                      user_query: str, 
                      files: List[Dict],
                      template_vars: Optional[Dict] = None) -> str:
        """
        Combine template, user query, and file information into final prompt
        
        Args:
            user_query (str): User's input query
            files (List[Dict]): List of available files
            template_vars (Dict, optional): Additional template variables
            
        Returns:
            str: Complete formatted prompt
        """
        # Format directory listing
        directory_list = self.format_directory_list(files)
        
        # Get the current template
        template = self.templates[self.current_template]
        
        # Prepare template variables
        vars_dict = {
            'user_query': user_query,
            'directory_list': directory_list
        }
        
        # Add any additional template variables
        if template_vars:
            vars_dict.update(template_vars)
        
        # Format the template with variables
        return template.format(**vars_dict)

    def add_custom_prompt(self, prompt: str) -> None:
        """
        Add a custom prompt to be included in the final prompt
        
        Args:
            prompt (str): Custom prompt to add
        """
        self.custom_prompts.append(prompt)

    def get_custom_prompts(self) -> List[str]:
        """
        Get all custom prompts
        
        Returns:
            List[str]: List of custom prompts
        """
        return self.custom_prompts.copy()

    def clear_custom_prompts(self) -> None:
        """Clear all custom prompts"""
        self.custom_prompts = []