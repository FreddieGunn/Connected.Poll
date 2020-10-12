from app import db, login, app
from flask_login import UserMixin
from datetime import datetime, timedelta
import hashlib
import string
import random
from time import time
import jwt
from sqlalchemy import func


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    forename = db.Column(db.String, index=True)
    surname = db.Column(db.String, index=True)
    username = db.Column(db.String, index=True, unique=True)
    email = db.Column(db.String, index=True, unique=True)
    salt = db.Column(db.String, index=True)
    password_hash = db.Column(db.String)

    polls = db.relationship('Poll', backref="creator", lazy="dynamic", cascade="all, delete, delete-orphan")
    responses = db.relationship('UserPollResponse', backref="UserResponses", lazy="dynamic")

    def set_password(self, password):
        self.salt = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(16))
        password += self.salt
        self.password_hash = hashlib.sha512(password.encode()).hexdigest()

    def check_password(self, password):
        password += self.salt
        return hashlib.sha512(password.encode()).hexdigest() == self.password_hash

    def __repr__(self):
        return'<User {}'.format(self.username)

    def get_polls(self):
        return Poll.query.join(User, (Poll.user_id == User.id)).filter(
            User.id == self.id).order_by(Poll.created_date.desc()).all()

    def get_reset_password_token(self, expires_in=900):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time()+expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


class Poll(db.Model):
    title = db.Column(db.String(64), index=True)
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    online = db.Column(db.Boolean, default=True, index=True)
    public = db.Column(db.Boolean, index=True)
    description = db.Column(db.String(128), index=True)

    questions = db.relationship('Question', backref='QForPoll', lazy="dynamic", cascade="all, delete, delete-orphan")
    responses = db.relationship('UserPollResponse', backref="PollResponses", lazy="dynamic",
                                cascade="all, delete, delete-orphan")

    def get_response_rate(self):
        response_rate = UserPollResponse.query.with_entities(func.strftime("%d/%m/%Y", UserPollResponse.date), func.count(
            UserPollResponse.id)).group_by(func.strftime("%Y-%m-%d", UserPollResponse.date)).filter_by(
            poll_id=self.id).all()

        # Below is used to add 0 figures for days where no responses have been submitted
        index = 1
        for response in response_rate:
            raw_response_date = datetime.strptime(response[0], "%d/%m/%Y")
            raw_tomorrow_date = raw_response_date + timedelta(days=1)
            if index == len(response_rate):
                break
            elif raw_tomorrow_date < datetime.strptime(response_rate[index][0], "%d/%m/%Y"):
                response_rate.insert(index, [raw_tomorrow_date.strftime("%d/%m/%Y"), 0])
            index += 1
        return response_rate


    def get_user_responses(self):
        responses = []
        for question in self.questions:
            temp = [question.question_title, question.type]
            if question.type != "textField":
                for answer in question.answers:
                    temp.append([answer.answer, len(answer.answers_from_user.all())])
            else:
                for user_answer in question.answers[0].answers_from_user:
                    temp.append(user_answer.user_answer)
            responses.append(temp)
        return responses

    def __repr__(self):
        return'<Poll {}'.format(self.id)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'))
    question_title = db.Column(db.String, index=True)
    type = db.Column(db.String, index=True)
    lower_label = db.Column(db.String, index=True)
    upper_label = db.Column(db.String, index=True)

    answers = db.relationship('Answer', backref="AForQ", lazy="dynamic", cascade="all, delete, delete-orphan")


class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    answer = db.Column(db.String, index=True)
    answers_from_user = db.relationship('UserAnswer', backref="AnswersFromUser", lazy="dynamic",
                                        cascade="all, delete, delete-orphan")


class UserPollResponse(db.Model):
    __tablename__ = 'userpollresponse'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'))
    date = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    response_answers = db.relationship('UserAnswer', backref="userResponses", lazy="dynamic",
                                       cascade="all, delete, delete-orphan")


class UserAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_poll_response_id = db.Column(db.Integer, db.ForeignKey('userpollresponse.id'))
    answer_id = db.Column(db.Integer, db.ForeignKey('answer.id'))
    user_answer = db.Column(db.String)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
