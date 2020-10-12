import xlsxwriter
from app import app, db
from app.models import User, Poll, Question, Answer, UserAnswer, UserPollResponse
from io import BytesIO


def create_excel(poll_id):
    types = {"sliderField": "Slider", "textField": "Text input", "radioField": "Single Choice",
             "checkField": "Multiple Choice"}
    poll = Poll.query.filter_by(id=poll_id).first()
    user_responses = UserPollResponse.query.filter_by(poll_id=poll_id).all()
    questions = poll.questions.all()

    # Generate new ordered response IDs as id in database are random large values
    generated_response_id = {}
    generated_question_id = {}
    response_id_counter = 1

    return_data = BytesIO()
    workbook = xlsxwriter.Workbook(return_data)
    bold = workbook.add_format({'bold': True})
    bold_bottom_border = workbook.add_format({'bottom': True, 'bold': True})
    date = workbook.add_format({'num_format': 'dd/mm/yy'})
    merge_format = workbook.add_format({
        "bold": True,
        "align": "center",
        "valign": "vcenter"
    })
    align_left = workbook.add_format({"align": "left"})
    # First worksheet (title page)
    worksheet = workbook.add_worksheet('Home')
    worksheet.set_column("B:E", 15)
    worksheet.merge_range("B3:C3", poll.title, merge_format)
    worksheet.merge_range("B5:C5", poll.description, merge_format)
    worksheet.write("B8", 'Responses:', bold)
    worksheet.write("B10", 'Created on:', bold)
    worksheet.write("B12", 'Available Publicly:', bold)

    worksheet.write("C8", len(user_responses))
    worksheet.write("C10", poll.created_date.strftime("%d/%m/%Y"))
    if poll.public:
        worksheet.write("C12", "Yes")
    else:
        worksheet.write('C12', "No")

    # Response worksheet
    response_page = workbook.add_worksheet("Responses")
    response_page.set_column("B:D", 15)
    response_page.write("B2", "Response ID", bold_bottom_border)
    response_page.write("C2", "Response Date", bold_bottom_border)
    row = 2

    for response in user_responses:
        generated_response_id[response.id] = response_id_counter
        response_page.write(row, 1, response_id_counter)
        response_page.write(row, 2, response.date, date)
        row += 1
        response_id_counter += 1

    question_id_counter = 1
    for question in questions:
        generated_question_id[question.id] = question_id_counter
        question_page = workbook.add_worksheet("Question "+str(question_id_counter))
        question_page.set_column("B:D", 15)
        question_page.write("B2", "Question:", bold)
        question_page.write("B3", "Type:", bold)
        question_page.write("B4", "Question ID:", bold)

        question_page.write("C2", question.question_title)
        question_page.write("C3", types[question.type])
        question_page.write("C4", question_id_counter, align_left)

        if question.type == "sliderField":
            question_page.write("B5", "Lower Label:", bold)
            question_page.write("B6", "Upper Label:", bold)
            question_page.write("C5", question.lower_label)
            question_page.write("C6", question.upper_label)

        if question.type == "textField":
            question_page.set_column("C:C", 60)
            question_page.write("B8", "Response ID", bold_bottom_border)
            question_page.write("C8", "Text Response", bold_bottom_border)
            answer_id = question.answers[0].id
            answers = UserAnswer.query.filter_by(answer_id=answer_id).all()
            row = 8
            for answer in answers:
                question_page.write(row, 1, generated_response_id[answer.user_poll_response_id])
                question_page.write(row, 2, answer.user_answer)
                row += 1

        else:
            question_page.write("B8", "Answer", bold_bottom_border)
            question_page.write("C8", "Responses", bold_bottom_border)
            row = 8
            for answer in question.answers:
                total = UserAnswer.query.filter_by(answer_id=answer.id).all()
                question_page.write(row, 1, answer.answer)
                question_page.write(row, 2, len(total))
                row += 1

        question_id_counter += 1

    worksheet = workbook.add_worksheet('All responses')
    worksheet.set_column("B:F", 15)
    worksheet.write("B2", "Response ID", bold_bottom_border)
    worksheet.write("C2", "Date", bold_bottom_border)
    worksheet.write("D2", "Question ID", bold_bottom_border)
    worksheet.write("E2", "Answer ID", bold_bottom_border)
    worksheet.write("F2", "Answer value", bold_bottom_border)
    row = 2
    for response in user_responses:
        for user_answer in response.response_answers.all():
            worksheet.write(row, 1, generated_response_id[response.id])
            worksheet.write(row, 2, response.date, date)
            question_id = Answer.query.filter_by(id=user_answer.answer_id).first().question_id
            worksheet.write(row, 3, generated_question_id[question_id])
            worksheet.write(row, 4, user_answer.answer_id)
            worksheet.write(row, 5, user_answer.user_answer)
            row += 1
    workbook.close()
    return return_data
