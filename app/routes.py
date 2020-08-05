from app import app, db
from flask import request, jsonify, make_response
from app.models import Message
import base64


users = {
    "ronica": "123",
    "amir": "321"
}


@app.errorhandler(Exception)
def all_exception_handler(error):
   return ('Error ' + f'{error}'), 500


def if_authenticated_return_username():
    if request.authorization:
        data = base64.b64decode((request.headers['authorization'].split(' ')[1]).encode('ascii')).decode('ascii')
        username, password = data.split(':', 1)
        if username in users and users.get(username) == password:
                return username
    return False


@app.route("/allMessages")
def all_messages():
    #the map function itarets on the query and then the lambda serializes each message and it's all wrapped with a list
    #because map return a map object
    return jsonify({'all messages': list(map(lambda mes: mes.serialize(), Message.query.all()))})


@app.route("/writeMessage", methods=['POST'])
def writeMessage():
    if if_authenticated_return_username():
        newMessage = Message(if_authenticated_return_username(), request.json['receiver'], request.json['subject'], request.json['message'])
        db.create_all()
        db.session.add(newMessage)
        db.session.commit()
        return jsonify({"new message created": newMessage.serialize()})
    return jsonify({"permission denied": True})


@app.route("/get_user_messages", methods=['GET'])
def get_messages():
    if if_authenticated_return_username():
        return jsonify({if_authenticated_return_username() + "'s messages": list(map(lambda mes: mes.serialize(), Message.query.filter_by(receiver=if_authenticated_return_username())))})
    return jsonify({"permission denied": True})


@app.route("/<string:user>/", methods=['GET'])
def get_user_messages(user):
    if if_authenticated_return_username() and if_authenticated_return_username() == user:
        return jsonify({user + "'s messages": list(map(lambda mes: mes.serialize(), Message.query.filter_by(receiver=user)))})
    return jsonify({"permission denied": True})


@app.route("/read/<int:message_id>", methods=['GET'])
def read_message(message_id):
    message = Message.query.get_or_404(message_id)
    if if_authenticated_return_username() and if_authenticated_return_username() == message.receiver:
        message.status = 'read'
        db.session.commit()
        return jsonify({"message read": message.serialize()})
    return jsonify({"permission denied": True})


@app.route("/unread", methods=['GET'])
def get_unread_messages():
    if if_authenticated_return_username():
        return jsonify({'unread messages for ' + if_authenticated_return_username(): list(map(lambda mes: mes.serialize(), Message.query.filter_by(receiver=if_authenticated_return_username(), status='unread')))})
    return jsonify({"permission denied": True})


@app.route("/<string:user>/unread", methods=['GET'])
def get_unread_user_messages(user):
    if if_authenticated_return_username() and if_authenticated_return_username() == user:
        return jsonify({'unread messages for ' + user: list(map(lambda mes: mes.serialize(), Message.query.filter_by(receiver=user, status='unread')))})
    return jsonify({"permission denied": True})


@app.route("/delete/<int:message_id>/", methods=['DELETE'])
def delete_message(message_id):
    message = Message.query.get_or_404(message_id)
    if if_authenticated_return_username() and if_authenticated_return_username() == message.sender or if_authenticated_return_username() == message.receiver:
        db.session.delete(message)
        db.session.commit()
        return jsonify({"deleted": True})
    return jsonify({"permission denied": True})
