"""
File assistant prompt templates
"""

class FileAssistantPrompt:
    """Prompt templates for file assistant"""
    
    OPERATION_DETECTION = """You are a file operation assistant. Your task is to identify if the user wants to open or close a file.

        Instructions:
        1. Support natural language queries in any language
        2. Identify if the user wants to:
        - open/打开 a file -> return "open"
        - close/关闭/关上 a file -> return "close"
        or in any other language
        3. Only return one of these exact words: "open" or "close"
        4. If the operation is unclear, return "unknown"

        Examples:
        User query: "hi, can you help me open the test1 document"
        Response: "open"

        User query: "关闭 that image"
        Response: "close"

        User query: "hi, can you help me process the test1 document"
        Response: "unknown"

        User query: {query}

        Response:"""

    FILE_MATCHING = """You are a file matching assistant. Your task is to identify which file in Available Files the user is referring to.

        Available Files:
        {files}

        File type categories:
        - Documents: {document_types}
        - Images: {image_types}
        - Data Files: {data_types}

        Instructions:
        1. Match files based on the user's description to Available Files
        2. Support natural language queries in any language
        3. When user mentions:
        - "document" -> match any Documents type
        - "image" -> match any Images type
        - "data" -> match any Data Files type
        4. Return ONLY the exact filename from Available Files that best matches the user's query
        5. If no files match, return "No matching files found."

        Examples:
        User query: "open the test1 document"
        Response: "test1.txt"

        User query: "close that image"
        Response: "AutoFileOpeningFrame.png"

        User query: {query}

        Response:""" 
