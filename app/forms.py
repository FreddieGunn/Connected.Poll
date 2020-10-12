from flask_wtf import FlaskForm
from wtforms import Form, StringField, PasswordField, BooleanField, SubmitField, FieldList, FormField, RadioField,\
    TextAreaField, HiddenField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Email, Length
from app.models import User
from flask_login import current_user


class FieldsRequiredForm(FlaskForm):

    class Meta:
        def render_field(self, field, render_kw):
            render_kw.setdefault('required', True)
            return super().render_field(field, render_kw)


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    forename = StringField('Forename', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm = PasswordField('Re-enter password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('This username is taken')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('This email is taken')

    def validate_password(self, password):
        if len(password.data) < 8:
            raise ValidationError('Password must be 8 characters or greater')


class EditAccountForm(FlaskForm):
    forename = StringField('Forename', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Confirm Changes')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('This username is taken, please try a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('This email is taken, please try a different one.')


class ChangePasswordForm(FlaskForm):
    current = PasswordField('Current Password', validators=[DataRequired()])
    new = PasswordField('New Password', validators=[DataRequired()])
    new2 = PasswordField('Re-enter New Password', validators=[DataRequired(),
                                                              EqualTo('new', message="Passwords don't match")])
    submit = SubmitField('Change Password')

    def validate_new(self, new):
        if len(new.data) < 8:
            raise ValidationError('Password must be 8 characters or greater')


class CreatePollAnswerForm(Form):
    answer = StringField('answer', validators=[DataRequired()])


# The code below is used to create each question
class CreateEachPollQuestionForm(Form):
    questionTitle = StringField('Question Title', validators=[DataRequired()])
    answerList = FieldList(FormField(CreatePollAnswerForm), min_entries=0)
    questionType = HiddenField('type')


class CreatePollForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=64, message="Title can only be 64 characters")])
    public = BooleanField('Make poll public?')
    description = TextAreaField('Description', validators=[Length(max=256,
                                                                  message="Description limited to 256 characters")])
    questionList = FieldList(FormField(CreateEachPollQuestionForm), min_entries=1)


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Reset Password Request')


class ResetPasswordForm(FlaskForm):
    new = PasswordField('New Password', validators=[DataRequired()])
    new2 = PasswordField('Re-enter New Password', validators=[DataRequired(), EqualTo('new',
                                                                                      message="Passwords don't match")])
    submit = SubmitField('Change Password')

    def validate_new(self, new):
        if len(new.data) < 8:
            raise ValidationError('Password must be 8 characters or greater')
