from flask import Flask, render_template, redirect, request
import connection
import data_manager
# import util
import util

app = Flask(__name__)
questions = connection.get_all_user_data(data_manager.QUESTION_FILE_PATH)
question_headers = data_manager.QUESTION_HEADER
answers = connection.get_all_user_data(data_manager.ANSWER_FILE_PATH)
answer_headers = data_manager.ANSWER_HEADER


@app.route("/")
def main():
    return render_template("list.html",
                           questions=sorted(questions, reverse=True, key=lambda item: int(item['vote_number'])),
                           question_headers=[" ".join(header.capitalize() for header in header.split("_"))
                                             for header in question_headers]
                           )


@app.route("/question/<question_id>")
def display_question(question_id):
    target_question = [question for question in questions if question['id'] == question_id][0]
    target_answers = [answer for answer in answers if answer['question_id'] == question_id]
    return render_template("question.html",
                           question=target_question,
                           answers=sorted(target_answers, key=lambda item: int(item['vote_number'])),
                           answer_headers=answer_headers,
                           question_id=question_id
                           )


@app.route("/add-question", methods=["GET", "POST"])
def add_question():
    if request.method == "POST":
        new_question = {}
        util.setup_dict(new_question, util.generate_id(), question_headers, request.form)
        connection.append_data(questions, new_question)
        connection.write_data_in_file(data_manager.QUESTION_FILE_PATH, questions, question_headers)
        return redirect("/question/" + new_question["id"])
    return render_template("add-question.html")


@app.route("/question/<question_id>/vote_up")
def vote_up_question(question_id):
    target_question = [question for question in questions if question['id'] == question_id][0]
    target_question["vote_number"] = str(int(target_question["vote_number"]) + 1)
    connection.write_data_in_file(data_manager.QUESTION_FILE_PATH, questions, question_headers)
    return redirect("/question/" + question_id)


@app.route("/question/<question_id>/vote_down")
def vote_down_question(question_id):
    target_question = [question for question in questions if question['id'] == question_id][0]
    target_question["vote_number"] = str(int(target_question["vote_number"]) - 1)
    connection.write_data_in_file(data_manager.QUESTION_FILE_PATH, questions, question_headers)
    return redirect("/question/" + question_id)


@app.route("/answer/<answer_id>/vote_up")
def vote_up_answer(answer_id):
    target_answer = [answer for answer in answers if answer['id'] == answer_id][0]
    target_answer["vote_number"] = str(int(target_answer["vote_number"]) + 1)
    connection.write_data_in_file(data_manager.ANSWER_FILE_PATH, answers, answer_headers)
    question_id = target_answer["question_id"]
    return redirect("/question/" + question_id)


@app.route("/answer/<answer_id>/vote_down")
def vote_down_answer(answer_id):
    target_answer = [answer for answer in answers if answer['id'] == answer_id][0]
    target_answer["vote_number"] = str(int(target_answer["vote_number"]) - 1)
    connection.write_data_in_file(data_manager.ANSWER_FILE_PATH, answers, answer_headers)
    question_id = target_answer["question_id"]
    return redirect("/question/" + question_id)


if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )
