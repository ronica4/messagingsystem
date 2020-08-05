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

def is_authenticated():
    if request.authorization:
        data = base64.b64decode((request.headers['authorization'].split(' ')[1]).encode('ascii')).decode('ascii')
        username, password = data.split(':', 1)
        if username in users:
            if users.get(username) == password:
                return username
            else:
                return False
        else:
            return False
    return False



@app.route("/test", methods=['GET', 'POST'])
def test():
    test = request.get_json()['hi']
    return test, 201

@app.route("/allMessages")
def all_messages():
    return jsonify({'all messages': list(map(lambda mes: mes.serialize(), Message.query.all()))})

@app.route("/writeMessage", methods=['POST'])
def writeMessage():
    if is_authenticated():
        newMessage = Message(is_authenticated(), request.json['receiver'], request.json['subject'], request.json['message'])
        db.create_all()
        db.session.add(newMessage)
        db.session.commit()
        return jsonify({"new message created": newMessage.serialize()})
    return jsonify({"permission denied": True})

@app.route("/get_user_messages", methods=['GET'])
def get_messages():
    #messages = Message.query.filter_by(sender=user)
    #messages = Message.query.all()
    #the map function itarets on the query and then the lambda serializes each message and it's all wrapped with a list
    #because we can't jsonify or serialize, so the map is converted to a list
    if is_authenticated():
        return jsonify({is_authenticated() + "'s messages": list(map(lambda mes: mes.serialize(), Message.query.filter_by(receiver=is_authenticated())))})
    return jsonify({"permission denied": True})


@app.route("/<string:user>/", methods=['GET'])
def get_user_messages(user):
    #messages = Message.query.filter_by(sender=user)
    #messages = Message.query.all()
    #the map function itarets on the query and then the lambda serializes each message and it's all wrapped with a list
    #because we can't jsonify or serialize, so the map is converted to a list
    if is_authenticated() and is_authenticated() == user:
        return jsonify({user + "'s messages": list(map(lambda mes: mes.serialize(), Message.query.filter_by(receiver=user)))})
    return jsonify({"permission denied": True})


@app.route("/read/<int:message_id>")
def read_message(message_id):
    message = Message.query.get_or_404(message_id)
    if is_authenticated() and is_authenticated() == message.receiver:
        message.status = 'read'
        db.session.commit()
        return jsonify({"message read": message.serialize()})
    return jsonify({"permission denied": True})



@app.route("/<string:user>/unread")
def get_unread_user_messages(user):
    if is_authenticated() and is_authenticated() == user:
        return jsonify({'unread messages for ' + user: list(map(lambda mes: mes.serialize(), Message.query.filter_by(receiver=user, status='unread')))})
    return jsonify({"permission denied": True})



@app.route("/delete/<int:message_id>/", methods=['DELETE'])
def delete_message(message_id):
    message = Message.query.get_or_404(message_id)
    if is_authenticated() and is_authenticated() == message.sender or is_authenticated() == message.receiver:
        db.session.delete(message)
        db.session.commit()
        return jsonify({"deleted": True})
    return jsonify({"permission denied": True})
