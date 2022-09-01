from flask import render_template, flash, redirect, url_for, request, send_file
from app import app, db
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm, RegistrationForm, EditAccountForm, ChangePasswordForm, CreatePollForm,\
    ResetPasswordRequestForm, ResetPasswordForm
from app.models import User, Poll, Question, Answer, UserAnswer, UserPollResponse
from werkzeug.urls import url_parse
from app.email import send_password_reset_email, password_changed_email, poll_created_email
from app.excel import create_excel


@app.route("/")
def home():
    return render_template('home.html')


@app.route("/create_poll", methods=['GET', 'POST'])
@login_required
def create_poll():
    form = CreatePollForm()
    if form.validate_on_submit():
        new_poll = Poll(title=form.title.data, public=form.public.data, description=form.description.data)
        current_user.polls.append(new_poll)

        for question in form.questionList.data:
            if question['questionType'] == "sliderField":

                new_question = Question(question_title=question['questionTitle'], type="sliderField",
                                        lower_label=question['answerList'][0]['answer'],
                                        upper_label=question['answerList'][1]['answer'])
                new_poll.questions.append(new_question)
                for num in range(1, 11):
                    new_answer = Answer(answer=num)
                    new_question.answers.append(new_answer)
            else:
                new_question = Question(question_title=question['questionTitle'], type=question['questionType'])
                new_poll.questions.append(new_question)

                if question['questionType'] == "textField":
                    new_answer = Answer(answer="text")
                    new_question.answers.append(new_answer)

                for answer in question['answerList']:
                    new_answer = Answer(answer=answer['answer'])
                    new_question.answers.append(new_answer)

        db.session.commit()
        poll_created_email(current_user, new_poll)
        return redirect(url_for('poll_preview', poll_id=new_poll.id))

    return render_template('create_poll.html', form=form)


@app.route("/my_polls")
@login_required
def my_polls():
    polls = current_user.polls
    return render_template('my_polls.html', polls=polls)


@app.route("/search_polls")
def search_polls():
    if current_user.is_authenticated:
        polls = db.session.query(Poll, User.username).join(User, (Poll.user_id == User.id)).filter(Poll.public == 1,
                            Poll.online == 1, Poll.user_id != current_user.id).order_by(Poll.created_date.desc()).all()
    else:
        polls = db.session.query(Poll, User.username).join(User, (Poll.user_id == User.id)).filter(Poll.public == 1,
                                            Poll.online == 1).order_by(Poll.created_date.desc()).all()

    return render_template('search_polls.html', polls=polls)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("my_account"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.lower()).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    return render_template('login.html', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/my_account", methods=['GET', 'POST'])
@login_required
def my_account():
    form = EditAccountForm(obj=current_user)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('You have successfully changed your details')
        return redirect(url_for('my_account'))
    return render_template('my_account.html', form=form)


@app.route("/create_account", methods=['GET', 'POST'])
def create_account():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(forename=form.forename.data, surname=form.surname.data, username=form.username.data.lower(),
                    email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('create_account.html', form=form)


@app.route("/change_password", methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current.data):
            flash('Password incorrect')
        elif form.new.data == form.current.data:
            flash('Password must be new')
        else:
            current_user.set_password(form.new.data)
            db.session.commit()
            flash('Password successfully changed')
        return redirect(url_for('change_password'))
    return render_template("change_password.html", form=form)


@app.route('/poll/<poll_id>', methods=["GET", "POST"])
def view_poll(poll_id):
    poll = Poll.query.filter_by(id=poll_id).first_or_404()
    if poll.online == 0:
        return render_template('my_poll_error.html', ErrorTitle="This poll no longer accepts responses")
    if current_user.is_authenticated:
        for response in current_user.responses:
            if response.poll_id == poll.id:
                return render_template('my_poll_error.html', ErrorTitle="You have already completed this form")
    message = ""

    if request.method == "POST":
        if current_user.is_authenticated:
            response = UserPollResponse(user_id=current_user.id, poll_id=poll.id)
            current_user.responses.append(response)
        else:
            response = UserPollResponse(poll_id=poll.id)
            db.session.add(response)

        index = 0
        for question in poll.questions:

            if question.type == "checkField":
                index2 = 0
                for answer in question.answers:
                    raw_answer = request.form.get('question-'+str(index)+"-answer-"+str(index2))
                    if raw_answer is not None:
                        user_answer = UserAnswer(answer_id=raw_answer)
                        response.response_answers.append(user_answer)
                    index2 += 1

            elif question.type == "textField":
                raw_answer = request.form['question-'+str(index)+'-answer']
                if raw_answer.isspace() or len(raw_answer) == 0:
                    message = "There was an error processing your response, please try again"

                user_answer = UserAnswer(user_answer=raw_answer, answer_id=question.answers[0].id)
                response.response_answers.append(user_answer)

            elif question.type == "radioField":
                raw_answer = request.form.get('question-' + str(index) + '-answer')
                if raw_answer is None:
                    message = "There was an error processing your response, please try again"
                user_answer = UserAnswer(answer_id=raw_answer)
                response.response_answers.append(user_answer)

            elif question.type == "sliderField":
                raw_answer = request.form['question-' + str(index) + '-answer']
                for answer in question.answers:
                    if answer.answer == raw_answer:
                        answer_id = answer.id
                user_answer = UserAnswer(answer_id=answer_id)
                response.response_answers.append(user_answer)
            index += 1
        db.session.commit()
        if message == "":
            return render_template('response_submitted.html')

    return render_template('view_poll.html', poll=poll, message=message)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('my_account'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            print("Email sent here")
        flash('Check your email for instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('my_account'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('home'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.new.data)
        db.session.commit()
        flash('Your password has been reset.')
        password_changed_email(user)
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@app.route('/poll_preview/<poll_id>')
@login_required
def poll_preview(poll_id):
    poll = Poll.query.filter_by(id=poll_id).first_or_404()
    if poll.user_id != current_user.id:
        return redirect(url_for('home'))
    return render_template('poll_preview.html', poll_id=poll_id, poll=poll)


@app.route('/my_polls/<poll_id>')
@login_required
def my_polls_results(poll_id):
    poll = Poll.query.filter_by(id=poll_id).first_or_404()
    response_rate = poll.get_response_rate()
    if len(response_rate) == 0:
        response_rate = ""
        question_responses = ""
    else:
        question_responses = poll.get_user_responses()
    if poll.user_id != current_user.id:
        return render_template("my_poll_error.html", ErrorTitle="You do not have access to view this polls results",
                               poll_id=poll_id, link=True)

    return render_template('my_poll_results.html', poll=poll, response_rate=response_rate,
                           question_responses=question_responses, poll_id=poll_id)


@app.route('/delete_poll/<poll_id>')
@login_required
def delete_poll(poll_id):
    poll = Poll.query.filter_by(id=poll_id).first_or_404()
    created_id = poll.user_id
    if created_id != current_user.id and current_user.id != 1:
        return render_template("my_poll_error.html", ErrorTitle="You do not own this poll")

    db.session.delete(poll)
    db.session.commit()
    flash('You deleted a poll')
    if current_user.id != 1:
        return redirect(url_for('my_polls'))
    else:
        return redirect(url_for('account_manager', user_id=created_id))


@app.route("/close_poll/<poll_id>")
@login_required
def close_poll(poll_id):
    poll = Poll.query.filter_by(id=poll_id).first_or_404()
    if poll.user_id != current_user.id:
        return render_template("my_poll_error.html", ErrorTitle="You do not own this poll")
    poll.online = 0
    db.session.commit()
    flash('This poll is now closed')
    return redirect(url_for('my_polls_results', poll_id=poll_id))


@app.route("/open_poll/<poll_id>")
@login_required
def open_poll(poll_id):
    poll = Poll.query.filter_by(id=poll_id).first_or_404()
    if poll.user_id != current_user.id:
        return render_template("my_poll_error.html", ErrorTitle="You do not own this poll")
    poll.online = 1
    db.session.commit()
    flash('This poll is now open')
    return redirect(url_for('my_polls_results', poll_id=poll_id))


@app.route("/private_poll/<poll_id>")
@login_required
def private_poll(poll_id):
    poll = Poll.query.filter_by(id=poll_id).first_or_404()
    if poll.user_id != current_user.id:
        return render_template("my_poll_error.html", ErrorTitle="You do not own this poll")
    poll.public = 0
    db.session.commit()
    flash('This poll is now private')
    return redirect(url_for('my_polls_results', poll_id=poll_id))


@app.route("/public_poll/<poll_id>")
@login_required
def public_poll(poll_id):
    poll = Poll.query.filter_by(id=poll_id).first_or_404()
    if poll.user_id != current_user.id:
        return render_template("my_poll_error.html", ErrorTitle="You do not own this poll")
    poll.public = 1
    db.session.commit()
    flash('This poll is now public')
    return redirect(url_for('my_polls_results', poll_id=poll_id))


@app.route('/excel/<poll_id>')
@login_required
def excel_download(poll_id):
    if Poll.query.filter_by(id=poll_id).first() is None:
        return render_template("my_poll_error.html", ErrorTitle="You do not own this poll")
    elif Poll.query.filter_by(id=poll_id).first().user_id != current_user.id:
        return render_template("my_poll_error.html", ErrorTitle="You do not own this poll")

    return_data = create_excel(poll_id)
    return_data.seek(0)
    return send_file(return_data, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, attachment_filename='ConnectedPoll-{id}.xlsx'.format(id=poll_id))


@app.route("/cv")
def cv_download():
    return send_file("static/FreddieGunnCV.docx", as_attachment=True, attachment_filename="FreddieGunnCV.docx")


@app.route("/admin")
@login_required
def admin():
    if current_user.id != 1:
        return redirect(url_for('home'))
    users = User.query.filter(User.id != 1).all()
    return render_template("admin.html", users=users)


@app.route("/admin/manage_<user_id>")
@login_required
def account_manager(user_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    if current_user.id != 1 or user.id == 1:
        return redirect(url_for('home'))
    return render_template("account_manager.html", user=user)


@app.route("/admin/delete_<user_id>")
@login_required
def delete_account(user_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    if current_user.id != 1 or user.id == 1:
        return redirect(url_for('home'))
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin'))
