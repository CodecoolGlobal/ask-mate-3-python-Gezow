from flask import Flask, render_template, redirect, request
import connection
import data_manager
import util
from datetime import datetime

app = Flask(__name__)
questions = connection.get_all_user_data(data_manager.QUESTION_FILE_PATH)
question_headers = data_manager.QUESTION_HEADER
answers = connection.get_all_user_data(data_manager.ANSWER_FILE_PATH)
answer_headers = data_manager.ANSWER_HEADER


@app.route("/")
def main():
    return render_template("list.html",
                           questions=sorted(questions, reverse=True, key=lambda item: item['submission_time']),
                           question_headers=[" ".join(header.capitalize() for header in header.split("_"))
                                             for header in question_headers]
                           )


@app.route("/question/<question_id>")
def display_question(question_id):
    target_question = util.generate_lst_of_targets(questions, question_id, 'id')[0]
    target_question["view_number"] = str(int(target_question["view_number"]) + 1)
    target_answers = util.generate_lst_of_targets(answers, question_id, "question_id")
    return render_template("question.html",
                           question=target_question,
                           answers=sorted(target_answers, reverse=True, key=lambda item: int(item['vote_number'])),
                           answer_headers=answer_headers,
                           question_id=question_id
                           )


@app.route("/add-question", methods=["GET", "POST"])
def add_question():
    if request.method == "POST":
        new_question = {}
        util.setting_up_dict(new_question, util.generate_id(), str(datetime.now()).split(".")[0], 0, None,
                             question_headers, request.form)
        connection.append_data(questions, new_question)
        connection.write_data_file(data_manager.QUESTION_FILE_PATH, questions, question_headers)
        return redirect("/question/" + new_question["id"])
    return render_template("add-question.html")


@app.route("/question/<question_id>/vote_up")
def vote_up_question(question_id):
    target_question = util.generate_lst_of_targets(questions, question_id, 'id')[0]
    target_question["vote_number"] = str(int(target_question["vote_number"]) + 1)
    connection.write_data_file(data_manager.QUESTION_FILE_PATH, questions, question_headers)
    return redirect("/question/" + question_id)


@app.route("/question/<question_id>/vote_down")
def vote_down_question(question_id):
    target_question = util.generate_lst_of_targets(questions, question_id, 'id')[0]
    target_question["vote_number"] = str(int(target_question["vote_number"]) - 1)
    connection.write_data_file(data_manager.QUESTION_FILE_PATH, questions, question_headers)
    return redirect("/question/" + question_id)


@app.route("/answer/<answer_id>/vote_up")
def vote_up_answer(answer_id):
    target_answer = util.generate_lst_of_targets(answers, answer_id, 'id')[0]
    target_answer["vote_number"] = str(int(target_answer["vote_number"]) + 1)
    connection.write_data_file(data_manager.ANSWER_FILE_PATH, answers, answer_headers)
    question_id = target_answer["question_id"]
    return redirect("/question/" + question_id)


@app.route("/answer/<answer_id>/vote_down")
def vote_down_answer(answer_id):
    target_answer = util.generate_lst_of_targets(answers, answer_id, 'id')[0]
    target_answer["vote_number"] = str(int(target_answer["vote_number"]) - 1)
    connection.write_data_file(data_manager.ANSWER_FILE_PATH, answers, answer_headers)
    question_id = target_answer["question_id"]
    return redirect("/question/" + question_id)


@app.route("/question/<question_id>/new_answer", methods=["GET", "POST"])
def add_answer(question_id):
    if request.method == "POST":
        new_answer = {}
        util.setting_up_dict(new_answer, util.generate_id(), str(datetime.now()).split(".")[0], 0, question_id,
                             answer_headers, request.form)
        connection.append_data(answers, new_answer)
        connection.write_data_file(data_manager.ANSWER_FILE_PATH, answers, answer_headers)
        return redirect("/question/" + question_id)
    return render_template("add-answer.html", question_id=question_id)


@app.route('/question/<question_id>/delete_question')
def delete_question(question_id):
    target_question = util.generate_lst_of_targets(questions, question_id, 'id')[0]
    questions.remove(target_question)
    connection.write_data_file(data_manager.QUESTION_FILE_PATH, questions, question_headers)
    for answer in answers:
        if answer['question_id'] == question_id:
            answers.remove(answer)
    connection.write_data_file(data_manager.ANSWER_FILE_PATH, answers, answer_headers)
    return redirect("/")


@app.route('/answer/<answer_id>/delete_answer')
def delete_answer(answer_id):
    target_answer = util.generate_lst_of_targets(answers, answer_id, 'id')[0]
    answers.remove(target_answer)
    connection.write_data_file(data_manager.ANSWER_FILE_PATH, answers, answer_headers)
    question_id = target_answer['question_id']
    return redirect("/question/" + question_id)


if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )
