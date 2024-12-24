from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для работы с клиентом

# Хранилище чатов
chats = {}

@app.route('/create_chat', methods=['POST'])
def create_chat():
    """
    Создаёт новый чат и возвращает его уникальный ID.
    """
    chat_id = str(len(chats) + 1).zfill(4)  # Уникальный ID
    chats[chat_id] = []  # Пустой список сообщений
    return jsonify({"chat_id": chat_id, "status": "success"})

@app.route('/send_message', methods=['POST'])
def send_message():
    """
    Обрабатывает отправку сообщения в чат.
    """
    data = request.json
    chat_id = data.get("chat_id")
    nickname = data.get("nickname")
    message = data.get("message")

    if chat_id in chats:
        chats[chat_id].append(f"{nickname}: {message}")
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "error", "message": "Chat not found"}), 404

@app.route('/get_chat', methods=['GET'])
def get_chat():
    """
    Возвращает историю сообщений по ID чата.
    """
    chat_id = request.args.get("chat_id")

    if chat_id in chats:
        return jsonify({"messages": chats[chat_id]})
    else:
        return jsonify({"status": "error", "message": "Chat not found"}), 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
