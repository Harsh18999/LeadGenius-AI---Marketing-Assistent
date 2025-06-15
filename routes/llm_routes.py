from flask import Blueprint, request, jsonify
import markdown
from services.llm_service import get_response_from_llm, get_bot_system_prompt

llm_bp = Blueprint('llm', __name__)

@llm_bp.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    query = data.get("query")
    domain = data.get("active_domain").replace('\n', '').replace(' ', '')
    companies_info = data.get("companies_info", {})

    if not query:
        return jsonify({"response": "Empty query received."})
    
    system_prompt = get_bot_system_prompt(content=companies_info.get(domain, {}).get('content', ''))
    
    try:
        reply = get_response_from_llm(
            prompt=query,
            system_prompt=system_prompt
        )
        return jsonify({"response": markdown.markdown(reply)})
    except Exception as e:
        print("LLM error:", e)
        return jsonify({"response": "Sorry, something went wrong while contacting the LLM."})