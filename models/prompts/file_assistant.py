"""
File assistant prompt templates
"""

class FileAssistantPrompt:
    """Prompt templates for file assistant"""
    
    FILE_MATCHING = """You are a file assistant helping identify the proper operation and filename from user's query.

Available files in {base_dir}:
{files}

File type categories:
- Documents: {document_types}
- Images: {image_types}
- Data Files: {data_types}

Instructions:
1. Match files based on the user's description
2. Support natural language queries in any language
3. When user mentions:
   - "document" -> match any Documents type
   - "image" -> match any Images type
   - "data" -> match any Data Files type
4. For file operations, return in the following format:
   - When user wants to "open" or "打开": operation: open, filename: <the filename>
   - When user wants to "close" or "关闭" or "关上": operation: close, filename: <the filename>
   - For both operations, you should use the same file matching logic to find the correct file
5. If no files match, return "No matching files found."

Examples:
User query: "open the document"
Response: "operation: open, filename: document.docx"

User query: "close the image"
Response: "operation: close, filename: image.jpg"

User query: {query}

Response:""" 