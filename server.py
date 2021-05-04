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
    return render_template("question.html",
                           question=target_question,
                           answers=target_answers,
                           answer_headers=data_manager.ANSWER_HEADER,
                           question_id=question_id,
                           IMAGE_DIR_PATH=data_manager.Q_IMAGE_DIR_PATH,
                           question_comments=data_manager.look_for_comments('comment', 'question_id', question_id)
                           )


@app.route("/add-question", methods=["GET", "POST"])
def add_question():
    if request.method == "POST":
        submission_time = str(datetime.now()).split(".")[0]
        title = request.form['title']
        message = request.form['message']
        data_manager.add_new_question(submission_time=submission_time,
                                      view_number=0,
                                      vote_number=0,
                                      title=title,
                                      message=message
                                      )
        new_question = data_manager.find_question_id(submission_time, title)
        if request.files['image']:
            filename = util.save_images(request.files, str(new_question["id"]), data_manager.Q_IMAGE_DIR_PATH)
        else:
            filename = ""
        data_manager.update_image(filename, new_question["id"], 'question')
        return redirect("/question/" + str(new_question["id"]))
    return render_template("add-question.html")


@app.route("/question/<question_id>/edit_question", methods=["GET", "POST"])
def edit_question(question_id):
    target_question = data_manager.find_target_question(question_id)[0]
    if request.method == "POST":
        if request.files['image']:
            filename = util.save_images(request.files, question_id, data_manager.Q_IMAGE_DIR_PATH)
        else:
            filename = target_question['image']
        title = request.form['title']
        message = request.form['message']
        data_manager.edit_question(question_id, title, message, filename)
        return redirect("/question/" + str(target_question['id']))
    return render_template("edit_question.html", question=target_question)


@app.route("/question/<question_id>/vote_up")
def vote_up_question(question_id):
    data_manager.vote(question_id, 'question', 1)
    return redirect("/question/" + question_id + "?voted=True")


@app.route("/question/<question_id>/vote_down")
def vote_down_question(question_id):
    data_manager.vote(question_id, 'question', -1)
    return redirect("/question/" + question_id + "?voted=True")


@app.route("/answer/<answer_id>/vote_up")
def vote_up_answer(answer_id):
    data_manager.vote(answer_id, 'answer', 1)
    question_id = data_manager.find_question_id_from_answer_id(answer_id)['question_id']
    return redirect("/question/" + str(question_id) + "?voted=True")


@app.route("/answer/<answer_id>/vote_down")
def vote_down_answer(answer_id):
    data_manager.vote(answer_id, 'answer', -1)
    question_id = data_manager.find_question_id_from_answer_id(answer_id)['question_id']
    return redirect("/question/" + str(question_id) + "?voted=True")


@app.route("/question/<question_id>/new_answer", methods=["GET", "POST"])
def add_answer(question_id):
    if request.method == "POST":
        submission_time = str(datetime.now()).split(".")[0]
        message = request.form['message']
        data_manager.add_new_answer(submission_time=submission_time,
                                    vote_number=0,
                                    question_id=question_id,
                                    message=message
                                    )
        new_answer = data_manager.find_answer_id(submission_time, message)
        if request.files['image']:
            filename = util.save_images(request.files, str(new_answer["id"]), data_manager.A_IMAGE_DIR_PATH)
        else:
            filename = ""
        data_manager.update_image(filename, new_answer["id"], 'answer')
        return redirect("/question/" + question_id)
    return render_template("add-answer.html", question_id=question_id)


@app.route('/question/<question_id>/delete_question')
def delete_question(question_id):
    target_answers = data_manager.find_answer_by_question_id(question_id)
    target_question = data_manager.find_target_question(question_id)[0]
    for answer in target_answers:
        if answer['image']:
            os.remove(data_manager.A_IMAGE_DIR_PATH + "/" + answer['image'])
    data_manager.delete_answers_by_question_id(question_id)
    if target_question['image']:
        os.remove(data_manager.Q_IMAGE_DIR_PATH + "/" + target_question['image'])
    data_manager.delete_from_db(question_id, 'question')
    return redirect("/")


@app.route('/answer/<answer_id>/delete_answer')
def delete_answer(answer_id):
    target_answer = data_manager.find_answer(answer_id)[0]
    if target_answer['image']:
        os.remove(data_manager.A_IMAGE_DIR_PATH + "/" + target_answer['image'])
    data_manager.delete_from_db(answer_id, 'answer')
    return redirect("/question/" + str(target_answer['question_id']))


@app.route('/question/<question_id>/new_comment', methods=['GET', 'POST'])
def new_comment_to_question(question_id):
    if request.method == 'POST':
        submission_time = str(datetime.now()).split(".")[0]
        data_manager.add_comment(question_id, 'null', request.form['message'], submission_time, 'null')
        return redirect("/question/" + question_id)
    return render_template('add-comment.html', question_id=question_id)


if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )
