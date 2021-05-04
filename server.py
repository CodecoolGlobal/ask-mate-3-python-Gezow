from flask import Flask, render_template, redirect, request, url_for
import connection
import data_manager
import util
from datetime import datetime
import os

app = Flask(__name__)


@app.route("/")
def main():
    if request.args.get("order_by") and request.args.get("order_direction") == "desc":
        sorted_questions = data_manager.get_ordered_questions_desc(request.args.get("order_by"))
        order = "asc"
    elif request.args.get("order_by") and request.args.get("order_direction") == "asc":
        sorted_questions = data_manager.get_ordered_questions_asc(request.args.get("order_by"))
        order = "desc"
    else:
        order = "asc"
        sorted_questions = data_manager.get_questions()
    return render_template("list.html",
                           questions=sorted_questions,
                           if_reversed=order,
                           question_headers=[" ".join(header.capitalize() for header in header.split("_"))
                                             for header in data_manager.QUESTION_HEADER]
                           )


@app.route("/question/<question_id>")
def display_question(question_id):
    if request.args.get("voted") != "True":
        data_manager.update_view_number(question_id)
    target_question = data_manager.find_target_question(question_id)[0]
    target_answers = data_manager.find_answers_to_question(question_id)
    print(target_question)
    return render_template("question.html",
                           question=target_question,
                           answers=target_answers,
                           answer_headers=data_manager.ANSWER_HEADER,
                           question_id=question_id,
                           IMAGE_DIR_PATH=data_manager.IMAGE_DIR_PATH
                           )


@app.route("/add-question", methods=["GET", "POST"])
def add_question():
    questions = connection.get_all_user_data(data_manager.QUESTION_FILE_PATH)
    if request.method == "POST":
        new_question = {}
        new_id = util.generate_id()
        if request.files['image']:
            filename = util.save_images(request.files, new_id)
        else:
            filename = None
        util.setting_up_dict(new_question, new_id, str(datetime.now()).split(".")[0], 0, 0, filename, None,
                             data_manager.QUESTION_HEADER, request.form)
        connection.append_data(questions, new_question)
        connection.write_data_file(data_manager.QUESTION_FILE_PATH, questions, data_manager.QUESTION_HEADER)
        return redirect("/question/" + new_question["id"])
    return render_template("add-question.html")


@app.route("/question/<question_id>/edit_question", methods=["GET", "POST"])
def edit_question(question_id):
    questions = connection.get_all_user_data(data_manager.QUESTION_FILE_PATH)
    target_question = util.generate_lst_of_targets(questions, question_id, 'id')[0]
    if request.method == "POST":
        if request.files['image']:
            filename = util.save_images(request.files, question_id)
        else:
            filename = target_question['image']
        util.setting_up_dict(target_question, question_id, target_question['submission_time'],
                             target_question['view_number'],
                             target_question['vote_number'], filename, None,
                             data_manager.QUESTION_HEADER, request.form)
        connection.write_data_file(data_manager.QUESTION_FILE_PATH, questions, data_manager.QUESTION_HEADER)
        return redirect("/question/" + target_question['id'])
    return render_template("edit_question.html", question=target_question)


@app.route("/question/<question_id>/vote_up")
def vote_up_question(question_id):
    questions = connection.get_all_user_data(data_manager.QUESTION_FILE_PATH)
    util.vote(questions, question_id, data_manager.QUESTION_FILE_PATH, data_manager.QUESTION_HEADER, 1)
    return redirect("/question/" + question_id + "?voted=True")


@app.route("/question/<question_id>/vote_down")
def vote_down_question(question_id):
    questions = connection.get_all_user_data(data_manager.QUESTION_FILE_PATH)
    util.vote(questions, question_id, data_manager.QUESTION_FILE_PATH, data_manager.QUESTION_HEADER, -1)
    return redirect("/question/" + question_id + "?voted=True")


@app.route("/answer/<answer_id>/vote_up")
def vote_up_answer(answer_id):
    answers = connection.get_all_user_data(data_manager.ANSWER_FILE_PATH)
    target_answer = util.vote(answers, answer_id, data_manager.ANSWER_FILE_PATH, data_manager.ANSWER_HEADER, 1)
    question_id = target_answer["question_id"]
    return redirect("/question/" + question_id + "?voted=True")


@app.route("/answer/<answer_id>/vote_down")
def vote_down_answer(answer_id):
    answers = connection.get_all_user_data(data_manager.ANSWER_FILE_PATH)
    target_answer = util.vote(answers, answer_id, data_manager.ANSWER_FILE_PATH, data_manager.ANSWER_HEADER, -1)
    question_id = target_answer["question_id"]
    return redirect("/question/" + question_id + "?voted=True")


@app.route("/question/<question_id>/new_answer", methods=["GET", "POST"])
def add_answer(question_id):
    answers = connection.get_all_user_data(data_manager.ANSWER_FILE_PATH)
    if request.method == "POST":
        new_answer = {}
        new_id = util.generate_id()
        if request.files['image']:
            filename = util.save_images(request.files, new_id)
        else:
            filename = None
        util.setting_up_dict(new_answer, new_id, str(datetime.now()).split(".")[0], 0, 0, filename, question_id,
                             data_manager.ANSWER_HEADER, request.form)
        connection.append_data(answers, new_answer)
        connection.write_data_file(data_manager.ANSWER_FILE_PATH, answers, data_manager.ANSWER_HEADER)
        return redirect("/question/" + question_id)
    return render_template("add-answer.html", question_id=question_id)


@app.route('/question/<question_id>/delete_question')
def delete_question(question_id):
    answers = connection.get_all_user_data(data_manager.ANSWER_FILE_PATH)
    questions = connection.get_all_user_data(data_manager.QUESTION_FILE_PATH)
    remaining_answers = []
    for answer in answers:
        if answer['question_id'] != question_id:
            remaining_answers.append(answer)
        else:
            if answer["image"]:
                os.remove(data_manager.IMAGE_DIR_PATH + "/" + answer['image'])
    connection.write_data_file(data_manager.ANSWER_FILE_PATH, remaining_answers, data_manager.ANSWER_HEADER)
    target_question = util.generate_lst_of_targets(questions, question_id, 'id')[0]
    if target_question['image']:
        os.remove(data_manager.IMAGE_DIR_PATH + "/" + target_question['image'])
    questions.remove(target_question)
    connection.write_data_file(data_manager.QUESTION_FILE_PATH, questions, data_manager.QUESTION_HEADER)
    return redirect("/")


@app.route('/answer/<answer_id>/delete_answer')
def delete_answer(answer_id):
    answers = connection.get_all_user_data(data_manager.ANSWER_FILE_PATH)
    target_answer = util.generate_lst_of_targets(answers, answer_id, 'id')[0]
    answers.remove(target_answer)
    connection.write_data_file(data_manager.ANSWER_FILE_PATH, answers, data_manager.ANSWER_HEADER)
    if target_answer['image']:
        os.remove(data_manager.IMAGE_DIR_PATH + "/" + target_answer['image'])
    question_id = target_answer['question_id']
    return redirect("/question/" + question_id)


if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )
