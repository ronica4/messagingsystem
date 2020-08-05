from app import db
from datetime import datetime
import pytz
from json import JSONEncoder
import json

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String, unique=False, nullable=False)
    receiver = db.Column(db.String, unique=False, nullable=False)
    subject = db.Column(db.String, unique=False, nullable=False)
    message = db.Column(db.Text, unique=False, nullable=False, default='')
    creationdate = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(pytz.timezone("Israel")))
    status = db.Column(db.String, unique=False, nullable=False, default='unread')

    def __init__(self, sender, receiver, subject, message):
        self.sender = sender
        self.receiver = receiver
        self.subject = subject
        self.message = message

    def serialize(self):
        return {"id": self.id,
                "creation date": self.creationdate,
                "sender": self.sender,
                "receiver": self.receiver,
                "subject": self.subject,
                "message": self.message}