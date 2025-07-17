# app.py
import os
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from datetime import timedelta
import ollama

from config import OLLAMA_MODEL, SYSTEM_PROMPT, MAX_TOKENS_CONTEXT

app = Flask(__name__)

# 🔐 Khoá session — đổi thành giá trị bí mật khi deploy
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-me")
app.permanent_session_lifetime = timedelta(days=7)

CORS(app, supports_credentials=True)

# --- Tiện ích lưu hội thoại ---
# session['chat_history'] = list[{role, content}]

def get_history():
    history = session.get("chat_history")
    if not history:
        history = [{"role": "system", "content": SYSTEM_PROMPT}]
        session["chat_history"] = history
    return history


def truncate_history_if_needed(history, limit_tokens=MAX_TOKENS_CONTEXT):
    # Ở đây ta ước lượng tokens đơn giản = số ký tự/4 (xấp xỉ)
    # Nếu dùng tokenizer thật (tiktoken / sentencepiece) thì chính xác hơn.
    est_tokens = sum(len(m["content"]) // 4 + 1 for m in history)
    if est_tokens <= limit_tokens:
        return history
    # Cắt bớt tin nhắn cũ, giữ system + gần nhất
    new_hist = [history[0]]  # system
    # lấy phần cuối cùng
    tail = []
    running = len(new_hist)
    for m in reversed(history[1:]):
        running += len(m["content"]) // 4 + 1
        tail.append(m)
        if running > limit_tokens:
            break
    new_hist.extend(reversed(tail))
    return new_hist


@app.route("/", methods=["GET"])
def index():
    # Render trang chat
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json(force=True)
    user_msg = (data.get("message") or "").strip()
    reset = data.get("reset", False)

    if reset:
        session.pop("chat_history", None)

    history = get_history()

    if user_msg:
        history.append({"role": "user", "content": user_msg})

    # Giới hạn kích thước context
    history = truncate_history_if_needed(history)
    session["chat_history"] = history

    # Gọi Ollama
    try:
        response = ollama.chat(model=OLLAMA_MODEL, messages=history)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    ai_text = response["message"]["content"]

    history.append({"role": "assistant", "content": ai_text})
    session["chat_history"] = history

    return jsonify({
        "reply": ai_text,
        "history": history[-10:],  # trả về 10 tin gần nhất cho frontend nhẹ
    })


@app.route("/api/reset", methods=["POST"])
def api_reset():
    session.pop("chat_history", None)
    history = get_history()  # tái tạo với system
    return jsonify({"status": "reset", "history": history})


if __name__ == "__main__":
    # Phát triển local
    # Flask reloader dùng threaded để tránh block khi gọi Ollama
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)