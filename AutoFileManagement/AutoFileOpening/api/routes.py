from flask import request, jsonify
from . import bp
from ..services.command import CommandService

@bp.route('/chat', methods=['POST'])
def chat():
    """
    Handle chat requests from the frontend.
    Combines custom prompts with user message and gets response from ChatGPT.
    """
    data = request.json
    message = data.get('message', '')
    
    command_service = CommandService()
    response = command_service.process_command(message)
    
    return jsonify(response)

 