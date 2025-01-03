from flask import request, jsonify
from . import bp
from ..services.command import CommandService

@bp.route('/chat', methods=['POST'])
async def chat():
    """
    Handle chat requests from the frontend.
    Combines custom prompts with user message and gets response from LLM.
    """
    data = request.json
    message = data.get('message', '')
    
    command_service = CommandService()
    response = await command_service.process_command(message)
    
    return jsonify(response)