import psycopg2
from flask import Flask, render_template, redirect, request, session, escape
from datetime import datetime
import os

import data_manager_universal
import data_manager_question
import data_manager_answer
import data_manager_tag
import data_manager_comment
import data_manager_users
import util


app = Flask(__name__)


@app.route("/")
def main():
    last_five_question = data_manager_question.get_ordered_questions("submission_time", 'DESC')[:5]
    return render_template("searched_list.html",
                           questions=last_five_question,
                           if_reversed='asc',
                           question_headers=[" ".join(header.capitalize() for header in header.split("_"))
                                             for header in data_manager_universal.QUESTION_HEADER])


@app.route("/list")
def display_list():
    if request.args.get("order_by") and request.args.get("order_direction") == "desc":
        sorted_questions = data_manager_question.get_ordered_questions(request.args.get("order_by"), 'DESC')
        order = "asc"
    elif request.args.get("order_by") and request.args.get("order_direction") == "asc":
        sorted_questions = data_manager_question.get_ordered_questions(request.args.get("order_by"), 'ASC')
        order = "desc"
    else:
        order = "asc"
        sorted_questions = data_manager_question.get_ordered_questions("submission_time", 'DESC')
    return render_template("list.html",
                           questions=sorted_questions,
                           if_reversed=order,
                           question_headers=[" ".join(header.capitalize() for header in header.split("_"))
                                             for header in data_manager_universal.QUESTION_HEADER]
                           )


@app.route("/question/<question_id>")
def display_question(question_id):
    if request.args.get("voted") != "True":
        data_manager_question.update_view_number(question_id)
    target_question = data_manager_universal.find_target(question_id, 'question')[0]
    target_answers = reversed(data_manager_answer.find_answers_to_question(question_id))
    relevant_tags = data_manager_tag.find_relevant_tags(question_id)
    return render_template("question.html",
                           question=target_question,
                           answers=target_answers,
                           answer_headers=data_manager_universal.ANSWER_HEADER,
                           question_id=question_id,
                           IMAGE_DIR_PATH=data_manager_universal.QUESTION_IMG_DIR_PATH,
                           question_comments=data_manager_universal.look_for_comments('comment', 'question_id',
                                                                                      question_id),
                           data_manager=data_manager_universal,
                           tags=relevant_tags
                           )


@app.route("/add-question", methods=["GET", "POST"])
def add_question():
    if request.method == "POST":
        submission_time = str(datetime.now()).split(".")[0]
        title = request.form['title']
        message = request.form['message'].replace("'", "`")
        active_user_id = data_manager_users.find_profile_id(escape(session['username']), 'username')['id']
        data_manager_question.add_new_question(submission_time=submission_time,
                                               view_number=0,
                                               vote_number=0,
                                               title=title,
                                               message=message,
                                               active_user_id=active_user_id
                                               )
        new_question = data_manager_question.find_question_id(submission_time, title)
        util.handle_images({"request_files": request.files,
                            "new_id": str(new_question["id"]),
                            "directory": data_manager_universal.QUESTION_IMG_DIR_PATH,
                            "else_filename": ""}, 'question')
        return redirect("/question/" + str(new_question["id"]) + "?voted=True")
    return render_template("add-question.html")


@app.route("/question/<question_id>/edit_question", methods=["GET", "POST"])
def edit_question(question_id):
    target_question = data_manager_universal.find_target(question_id, 'question')[0]
    if request.method == "POST":
        util.handle_images({"request_files": request.files,
                            "new_id": question_id,
                            "directory": data_manager_universal.QUESTION_IMG_DIR_PATH,
                            "else_filename": target_question['image']}, 'question')
        title = request.form['title']
        message = request.form['message'].replace("'", "`")
        data_manager_question.edit_question(question_id, title, message)
        return redirect("/question/" + str(target_question['id']) + "?voted=True")
    return render_template("edit_question.html", question=target_question)


@app.route("/question/<question_id>/vote_up")
def vote_up_question(question_id):
    data_manager_universal.vote(question_id, 'question', 1)
    return redirect("/question/" + question_id + "?voted=True")


@app.route("/question/<question_id>/vote_down")
def vote_down_question(question_id):
    data_manager_universal.vote(question_id, 'question', -1)
    return redirect("/question/" + question_id + "?voted=True")


@app.route("/answer/<answer_id>/vote_up")
def vote_up_answer(answer_id):
    data_manager_universal.vote(answer_id, 'answer', 1)
    question_id = data_manager_answer.find_question_id_from_answer_id(answer_id)['question_id']
    return redirect("/question/" + str(question_id) + "?voted=True")


@app.route("/answer/<answer_id>/vote_down")
def vote_down_answer(answer_id):
    data_manager_universal.vote(answer_id, 'answer', -1)
    question_id = data_manager_answer.find_question_id_from_answer_id(answer_id)['question_id']
    return redirect("/question/" + str(question_id) + "?voted=True")


@app.route("/question/<question_id>/new_answer", methods=["GET", "POST"])
def add_answer(question_id):
    if request.method == "POST":
        submission_time = str(datetime.now()).split(".")[0]
        message = request.form['message'].replace("'", "`")
        data_manager_answer.add_new_answer(submission_time=submission_time,
                                           vote_number=0,
                                           question_id=question_id,
                                           message=message
                                           )
        new_answer = data_manager_answer.find_answer_id(submission_time, message)
        util.handle_images({"request_files": request.files,
                            "new_id": str(new_answer["id"]),
                            "directory": data_manager_universal.ANSWER_IMG_DIR_PATH,
                            "else_filename": ""}, 'answer')
        return redirect("/question/" + question_id + "?voted=True")
    return render_template("add-answer.html", question_id=question_id)


@app.route('/question/<question_id>/delete_question')
def delete_question(question_id):
    target_answers = data_manager_answer.find_answer_by_question_id(question_id)
    target_question = data_manager_universal.find_target(question_id, 'question')[0]
    for answer in target_answers:
        if answer['image']:
            os.remove(data_manager_universal.ANSWER_IMG_DIR_PATH + "/" + answer['image'])
    data_manager_answer.delete_answers_by_question_id(question_id)
    if target_question['image']:
        os.remove(data_manager_universal.QUESTION_IMG_DIR_PATH + "/" + target_question['image'])
    data_manager_universal.delete_from_db(question_id, 'question')
    return redirect("/list")


@app.route('/answer/<answer_id>/delete_answer')
def delete_answer(answer_id):
    target_answer = data_manager_universal.find_target(answer_id, 'answer')[0]
    if target_answer['image']:
        os.remove(data_manager_universal.ANSWER_IMG_DIR_PATH + "/" + target_answer['image'])
    data_manager_universal.delete_from_db(answer_id, 'answer')
    return redirect("/question/" + str(target_answer['question_id']) + "?voted=True")


@app.route('/question/<question_id>/new_comment', methods=['GET', 'POST'])
def new_comment_to_question(question_id):
    if request.method == 'POST':
        submission_time = str(datetime.now()).split(".")[0]
        data_manager_comment.add_comment(
            question_id, 'null', request.form['message'].replace("'", "`"), submission_time, 'null')
        return redirect("/question/" + question_id + "?voted=True")
    return render_template('add-comment.html', question_id=question_id)


@app.route("/answer/<answer_id>/new_comment", methods=["GET", "POST"])
def add_comment_to_answer(answer_id):
    q_id = data_manager_answer.find_question_id_from_answer_id(answer_id)['question_id']
    if request.method == 'POST':
        submission_time = str(datetime.now()).split(".")[0]
        data_manager_comment.add_comment('null', answer_id, request.form["message"].replace("'", "`"),
                                         submission_time, 'null')
        return redirect("/question/" + str(q_id) + "?voted=True")
    return render_template('add-comment-answer.html',
                           answer_id=answer_id,
                           question_id=q_id
                           )


@app.route("/search")
def search_in_questions():
    if request.args.get("q"):
        relevant_questions = data_manager_question.filter_questions(request.args.get("q"))
        return render_template("searched_list.html",
                               questions=relevant_questions,
                               if_reversed="asc",
                               question_headers=[" ".join(header.capitalize() for header in header.split("_"))
                                                 for header in data_manager_universal.QUESTION_HEADER]
                               )


@app.route("/answer/<answer_id>/edit", methods=["GET", "POST"])
def edit_answer(answer_id):
    target_answer = data_manager_universal.find_target(answer_id, 'answer')[0]
    if request.method == "POST":
        util.handle_images({"request_files": request.files,
                            "new_id": str(target_answer["id"]),
                            "directory": data_manager_universal.ANSWER_IMG_DIR_PATH,
                            "else_filename": target_answer["image"]}, 'answer')
        message = request.form['message'].replace("'", "`")
        data_manager_answer.edit_answer(answer_id, message)
        return redirect("/question/" + str(target_answer['question_id']) + "?voted=True")
    return render_template("edit_a.html", a_or_c=target_answer)


@app.route("/comment/<comment_id>/edit", methods=["GET", "POST"])
def edit_comment(comment_id):
    target_comment = data_manager_comment.find_comment(comment_id)[0]
    if request.method == "POST":
        data_manager_comment.update_edited_count(comment_id)
        message = request.form['message'].replace("'", "`")
        data_manager_comment.edit_comment(comment_id, message)
        return util.redirect_after_comment_action(target_comment)
    return render_template("edit_c.html", a_or_c=target_comment)


@app.route("/comment/<comment_id>/delete")
def delete_comment(comment_id):
    target_comment = data_manager_comment.find_comment(comment_id)[0]
    data_manager_universal.delete_from_db(comment_id, 'comment')
    return util.redirect_after_comment_action(target_comment)


@app.route("/question/<question_id>/new_tag", methods=["GET", "POST"])
def add_tag(question_id):
    if request.method == "POST":
        try:
            if request.form['message']:
                data_manager_tag.add_new_tag(request.form['message'].replace("'", "`"))
                target_tag = data_manager_tag.find_tag_id(request.form['message'].replace("'", "`"))['id']
            else:
                target_tag = data_manager_tag.find_tag_id(request.form['tag-name'])['id']
            data_manager_tag.choose_tag(question_id, target_tag)
            return redirect("/question/" + question_id + "?voted=True")
        except psycopg2.Error as error:
            return render_template("error.html", error_code=error.pgcode)
    all_tags = data_manager_tag.all_tags()
    return render_template("add_tag.html", all_tags=all_tags, question_id=question_id)


@app.route("/question/<question_id>/tag/<tag_id>/delete")
def delete_tag(question_id, tag_id):
    data_manager_tag.delete_tag(question_id, tag_id)
    return redirect("/question/" + question_id + "?voted=True")


@app.route("/sign-up", methods=["GET", "POST"])
def registration():
    if 'email' not in session and 'password' not in session:
        if request.method == "POST":
            user_emails, user_names = [email["email"] for email in data_manager_users.get_user_info('email')], \
                                [username["username"] for username in data_manager_users.get_user_info('username')]
            if request.form['email'] not in user_emails and request.form['username'] not in user_names:
                data_manager_users.add_new_user({'email': request.form["email"].replace("'", "`"),
                                                 'password': util.hash_password(request.form["password"]),
                                                 'username': request.form["username"].replace("'", "`"),
                                                 'reputation': 0,
                                                 'image': 'null'}
                                                )
                new_profile = data_manager_users.find_profile_id(request.form["email"], 'email')
                util.handle_images({"request_files": request.files,
                                    "new_id": str(new_profile["id"]),
                                    "directory": data_manager_universal.PROFILE_IMG_DIR_PATH,
                                    "else_filename": ""}, 'users')
                return redirect("/")
            return render_template("error.html", error_code='Email address or user name already in use!')
        return render_template("sign-up.html")
    return render_template("error.html", error_code='You are already signed up and logged in!')


@app.route("/users")
def users():
    if request.args.get("order_by") and request.args.get("order_direction") == "desc":
        sorted_users = data_manager_users.get_ordered_users(request.args.get("order_by"), 'DESC')
        order = "asc"
    elif request.args.get("order_by") and request.args.get("order_direction") == "asc":
        sorted_users = data_manager_users.get_ordered_users(request.args.get("order_by"), 'ASC')
        order = "desc"
    else:
        order = "asc"
        sorted_users = data_manager_users.get_ordered_users("username", 'DESC')
    return render_template("users_list.html",
                           users=sorted_users,
                           if_reversed=order,
                           user_headers=[" ".join(header.capitalize() for header in header.split("_"))
                                             for header in data_manager_universal.USER_HEADER]
                           )


if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )
