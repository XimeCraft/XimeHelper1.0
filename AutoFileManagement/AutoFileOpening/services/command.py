from .chat import ChatService
from .prompt import PromptService
from .file_service import FileService

class CommandService:
    def __init__(self):
        self.chat_service = ChatService()
        self.prompt_service = PromptService()
        self.file_service = FileService()
    
    def process_command(self, user_message):
        """
        Process user command and execute corresponding actions
        """
        try:
            # Get list of available files
            files = self.file_service.get_files()
            
            # Add file information to prompt
            files_info = "\nAvailable files:\n" + "\n".join(
                [f"- {f['name']} ({f['type']})" for f in files]
            )
            
            # Combine everything into the prompt
            prompt = self.prompt_service.combine_prompt(user_message + files_info)
            
            # Get response from ChatGPT
            response = self.chat_service.get_response(prompt)
            
            # Parse response and execute commands (you can add this logic later)
            # For example, if response contains "open file xxx", call file_service.open_file()
            
            return {
                'response': response,
                'files': files
            }
            
        except Exception as e:
            # Handle errors appropriately
            print(f"Error in CommandService: {str(e)}")
            return {
                'error': str(e),
                'response': "Sorry, I encountered an error processing your command."
            } 