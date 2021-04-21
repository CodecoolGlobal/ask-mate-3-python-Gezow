from flask import Flask, render_template, redirect, request, url_for
import connection
import data_manager
import util
from datetime import datetime
import os


app = Flask(__name__)


@app.route("/")
def main():
    questions = connection.get_all_user_data(data_manager.QUESTION_FILE_PATH)
    if request.args.get("order_by") == "submission_time" and request.args.get("order_direction") == "desc":
        sorted_questions = sorted(questions, reverse=True, key=lambda item: item['submission_time'])
        order = "asc"
    elif request.args.get("order_by") == "submission_time" and request.args.get("order_direction") == "asc":
        sorted_questions = sorted(questions, key=lambda item: item['submission_time'])
        order = "desc"
    elif request.args.get("order_by") == "view_number" and request.args.get("order_direction") == "desc":
        sorted_questions = sorted(questions, reverse=True, key=lambda item: int(item['view_number']))
        order = "asc"
    elif request.args.get("order_by") == "view_number" and request.args.get("order_direction") == "asc":
        sorted_questions = sorted(questions, key=lambda item: int(item['view_number']))
        order = "desc"
    elif request.args.get("order_by") == "vote_number" and request.args.get("order_direction") == "desc":
        sorted_questions = sorted(questions, reverse=True, key=lambda item: int(item['vote_number']))
        order = "asc"
    elif request.args.get("order_by") == "vote_number" and request.args.get("order_direction") == "asc":
        sorted_questions = sorted(questions, key=lambda item: int(item['vote_number']))
        order = "desc"
    elif request.args.get("order_by") == "title" and request.args.get("order_direction") == "desc":
        sorted_questions = sorted(questions, reverse=True, key=lambda item: item['title'])
        order = "asc"
    elif request.args.get("order_by") == "title" and request.args.get("order_direction") == "asc":
        sorted_questions = sorted(questions, key=lambda item: item['title'])
        order = "desc"
    elif request.args.get("order_by") == "message" and request.args.get("order_direction") == "desc":
        sorted_questions = sorted(questions, reverse=True, key=lambda item: item['message'])
        order = "asc"
    elif request.args.get("order_by") == "message" and request.args.get("order_direction") == "asc":
        sorted_questions = sorted(questions, key=lambda item: item['message'])
        order = "desc"
    else:
        order = "asc"
        sorted_questions = sorted(questions, reverse=True, key=lambda item: item['submission_time'])
    return render_template("list.html",
                           questions=sorted_questions,
                           if_reversed=order,
                           question_headers=[" ".join(header.capitalize() for header in header.split("_"))
                                             for header in data_manager.QUESTION_HEADER]
                           )


@app.route("/question/<question_id>")
def display_question(question_id):
    questions = connection.get_all_user_data(data_manager.QUESTION_FILE_PATH)
    answers = connection.get_all_user_data(data_manager.ANSWER_FILE_PATH)
    target_question = util.generate_lst_of_targets(questions, question_id, 'id')[0]
    if request.args.get("voted") != "True":
        target_question["view_number"] = str(int(target_question["view_number"]) + 1)
        connection.write_data_file(data_manager.QUESTION_FILE_PATH, questions, data_manager.QUESTION_HEADER)
    target_answers = util.generate_lst_of_targets(answers, question_id, "question_id")
    return render_template("question.html",
                           question=target_question,
                           answers=sorted(target_answers, reverse=True, key=lambda item: int(item['vote_number'])),
                           answer_headers=data_manager.ANSWER_HEADER,
                           question_id=question_id,
                           IMAGE_DIR_PATH=data_manager.IMAGE_DIR_PATH
                           )


@app.route("/add-question", methods=["GET", "POST"])
def add_question():
    images = data_manager.IMAGE_DIR_PATH
    questions = connection.get_all_user_data(data_manager.QUESTION_FILE_PATH)
    if request.method == "POST":
        new_question = {}
        new_id = util.generate_id()
        if request.files["image"]:
            image = request.files['image']
            filename = new_id + "." + "".join(image.filename.split(".")[1])
            image.save(os.path.join(images, filename))
        else:
            filename = None
        util.setting_up_dict(new_question, new_id, str(datetime.now()).split(".")[0], 0, filename, None,
                             data_manager.QUESTION_HEADER, request.form)
        connection.append_data(questions, new_question)
        connection.write_data_file(data_manager.QUESTION_FILE_PATH, questions, data_manager.QUESTION_HEADER)
        return redirect("/question/" + new_question["id"])
    return render_template("add-question.html")


@app.route("/question/<question_id>/vote_up")
def vote_up_question(question_id):
    questions = connection.get_all_user_data(data_manager.QUESTION_FILE_PATH)
    target_question = util.generate_lst_of_targets(questions, question_id, 'id')[0]
    target_question["vote_number"] = str(int(target_question["vote_number"]) + 1)
    connection.write_data_file(data_manager.QUESTION_FILE_PATH, questions, data_manager.QUESTION_HEADER)
    return redirect("/question/" + question_id + "?voted=True")


@app.route("/question/<question_id>/vote_down")
def vote_down_question(question_id):
    questions = connection.get_all_user_data(data_manager.QUESTION_FILE_PATH)
    target_question = util.generate_lst_of_targets(questions, question_id, 'id')[0]
    target_question["vote_number"] = str(int(target_question["vote_number"]) - 1)
    connection.write_data_file(data_manager.QUESTION_FILE_PATH, questions, data_manager.QUESTION_HEADER)
    return redirect("/question/" + question_id + "?voted=True")


@app.route("/answer/<answer_id>/vote_up")
def vote_up_answer(answer_id):
    answers = connection.get_all_user_data(data_manager.ANSWER_FILE_PATH)
    target_answer = util.generate_lst_of_targets(answers, answer_id, 'id')[0]
    target_answer["vote_number"] = str(int(target_answer["vote_number"]) + 1)
    connection.write_data_file(data_manager.ANSWER_FILE_PATH, answers, data_manager.ANSWER_HEADER)
    question_id = target_answer["question_id"]
    return redirect("/question/" + question_id + "?voted=True")


@app.route("/answer/<answer_id>/vote_down")
def vote_down_answer(answer_id):
    answers = connection.get_all_user_data(data_manager.ANSWER_FILE_PATH)
    target_answer = util.generate_lst_of_targets(answers, answer_id, 'id')[0]
    target_answer["vote_number"] = str(int(target_answer["vote_number"]) - 1)
    connection.write_data_file(data_manager.ANSWER_FILE_PATH, answers, data_manager.ANSWER_HEADER)
    question_id = target_answer["question_id"]
    return redirect("/question/" + question_id + "?voted=True")


@app.route("/question/<question_id>/new_answer", methods=["GET", "POST"])
def add_answer(question_id):
    answers = connection.get_all_user_data(data_manager.ANSWER_FILE_PATH)
    if request.method == "POST":
        new_answer = {}
        util.setting_up_dict(new_answer, util.generate_id(), str(datetime.now()).split(".")[0], 0, question_id,
                             data_manager.ANSWER_HEADER, request.form)
        connection.append_data(answers, new_answer)
        connection.write_data_file(data_manager.ANSWER_FILE_PATH, answers, data_manager.ANSWER_HEADER)
        return redirect("/question/" + question_id)
    return render_template("add-answer.html", question_id=question_id)


@app.route('/question/<question_id>/delete_question')
def delete_question(question_id):
    answers = connection.get_all_user_data(data_manager.ANSWER_FILE_PATH)
    questions = connection.get_all_user_data(data_manager.QUESTION_FILE_PATH)
    answers_back = []
    for answer in answers:
        if answer['question_id'] != question_id:
            answers_back.append(answer)
    connection.write_data_file(data_manager.ANSWER_FILE_PATH, answers_back, data_manager.ANSWER_HEADER)
    target_question = util.generate_lst_of_targets(questions, question_id, 'id')[0]
    questions.remove(target_question)
    connection.write_data_file(data_manager.QUESTION_FILE_PATH, questions, data_manager.QUESTION_HEADER)
    return redirect("/")


@app.route('/answer/<answer_id>/delete_answer')
def delete_answer(answer_id):
    answers = connection.get_all_user_data(data_manager.ANSWER_FILE_PATH)
    target_answer = util.generate_lst_of_targets(answers, answer_id, 'id')[0]
    answers.remove(target_answer)
    connection.write_data_file(data_manager.ANSWER_FILE_PATH, answers, data_manager.ANSWER_HEADER)
    question_id = target_answer['question_id']
    return redirect("/question/" + question_id)


if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )
