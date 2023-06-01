from flask import Flask, render_template, request
from flask_socketio import SocketIO
import openai

app = Flask(__name__)
socketio = SocketIO(app, manage_session=False)
openai.api_key = "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"


@app.route("/")
def index():
    return render_template("index.html")


def generate_response(message, sid):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are an AI tutor specializing in Kumon math method. Your role includes explaining various mathematical units as if you were teaching an elementary school student, providing explanations that include examples, necessary concepts, and key points for problem-solving. When giving examples, perform the mathematical calculations first and provide explanations in a new line afterwards. You are also capable of conducting further dialogues with users to answer any additional inquiries related to their studies. When a mathematical term is mentioned in a question, generate a list of related topics for the user to choose from, to better specify their query.",
            },
            {"role": "user", "content": message},
        ],
        max_tokens=2000,
        stream=True,
    )

    for response_message in response:
        socketio.emit("ai_message", {"message": response_message}, room=sid)
    # Once the loop is done, send a completion message
    socketio.emit("ai_message_complete", room=sid)


@socketio.on("message")
def handle_message(data):
    user_message = data["message"]
    sid = request.sid
    socketio.emit("user_message", data, room=sid)
    socketio.start_background_task(generate_response, user_message, sid)


if __name__ == "__main__":
    socketio.run(app)
