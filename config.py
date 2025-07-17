# config.py
OLLAMA_MODEL = "llama3"  # đổi sang model bạn đã pull: llama3, mistral, gemma...
SYSTEM_PROMPT = "Bạn là trợ lý AI thông minh, luôn trả lời bằng tiếng Việt."
MAX_TOKENS_CONTEXT = 20000  # Giới hạn số token/context lưu (cắt bớt lịch sử nếu quá dài)