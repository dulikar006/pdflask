# app.py
import uuid

from flask import Flask, request, jsonify

from mac_convo_streamlit import run_agents

app = Flask(__name__)

chat_messages = []


@app.route('/send', methods=['POST'])
def send_message():
    data = request.json
    person = data.get('person')
    message = data.get('message')
    if message:
        print(message)
        chat_messages.append({"guid": str(uuid.uuid4()), "person": person, "message": message})
        return jsonify({'status': 'success', "person": person, "message": message}), 200
    return jsonify({'status': 'error', 'message': 'No message provided'}), 400


@app.route('/messages', methods=['GET'])
def get_messages():
    return jsonify(chat_messages), 200


@app.route('/clear', methods=['GET'])
def get_clear():
    chat_messages.clear()
    print("messages_cleared")
    return jsonify({'status': 'success'}), 200


@app.route('/start', methods=['POST'])
def start_debate():
    data = request.json
    question = data.get('question')
    run_agents(question)
    return jsonify({'status': 'success'}), 200


if __name__ == '__main__':
    app.run()
