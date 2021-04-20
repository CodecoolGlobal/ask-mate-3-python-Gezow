from flask import Flask, render_template, redirect
import connection
import data_manager
# import util


app = Flask(__name__)
questions = connection.get_all_user_data(data_manager.QUESTION_FILE_PATH)
question_headers = data_manager.QUESTION_HEADER
answers = connection.get_all_user_data(data_manager.ANSWER_FILE_PATH)
answer_headers = data_manager.ANSWER_HEADER


@app.route("/")
def main():
    return render_template("list.html",
                           questions=questions,
                           question_headers=[" ".join(header.capitalize() for header in header.split("_"))
                                             for header in question_headers]
                           )


@app.route("/question/<question_id>")
def display_question(question_id):
    target_question = [question for question in questions if question['id'] == question_id][0]
    target_answers = [answer for answer in answers if answer['question_id'] == question_id]
    return render_template("question.html",
                           question=target_question,
                           answers=target_answers,
                           answer_headers=answer_headers
                           )


if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )
