import psycopg2
from flask import Flask, render_template, redirect, request, session, escape, url_for
from datetime import datetime
import os

from data_managers import data_manager_universal, data_manager_questions, data_manager_answers, data_manager_tags, \
    data_manager_comments, data_manager_users
import util


app = Flask(__name__)
app.secret_key = b'secretkey'


@app.route("/")
def main():
    logged_in = True if "username" in session else False
    username = session["username"] if logged_in else None
    return render_template("list_searched.html",
                           questions=data_manager_questions.get_ordered_questions("submission_time", 'DESC')[:5],
                           if_reversed='asc',
                           question_headers=[" ".join(header.capitalize() for header in header.split("_"))
                                             for header in data_manager_universal.QUESTION_HEADER],
                           logged_in=logged_in,
                           username=username
                           )


@app.route("/list")
def display_list():
    logged_in = True if "username" in session else False
    username = session["username"] if logged_in else None
    if request.args.get("order_by") and request.args.get("order_direction") == "desc":
        sorted_questions = data_manager_questions.get_ordered_questions(request.args.get("order_by"), 'DESC')
        order = "asc"
    elif request.args.get("order_by") and request.args.get("order_direction") == "asc":
        sorted_questions = data_manager_questions.get_ordered_questions(request.args.get("order_by"), 'ASC')
        order = "desc"
    else:
        order = "asc"
        sorted_questions = data_manager_questions.get_ordered_questions("submission_time", 'DESC')
    return render_template("list.html",
                           questions=sorted_questions,
                           if_reversed=order,
                           question_headers=[" ".join(header.capitalize() for header in header.split("_"))
                                             for header in data_manager_universal.QUESTION_HEADER],
                           logged_in=logged_in,
                           username=username
                           )


@app.route("/question/<question_id>")
def display_question(question_id):
    logged_in = True if "username" in session else False
    username = session["username"] if logged_in else "None"
    try:
        if request.args.get("voted") != "True":
            data_manager_questions.update_view_number(question_id)
        target_question = data_manager_universal.find_target(question_id, 'id', 'questions')[0]
        target_answers = reversed(data_manager_answers.find_answers_to_question(question_id))
        relevant_tags = data_manager_tags.find_relevant_tags(question_id)
        return render_template("question.html",
                               question=target_question,
                               answers=target_answers,
                               answer_headers=data_manager_universal.ANSWER_HEADER,
                               question_id=question_id,
                               IMAGE_DIR_PATH=data_manager_universal.QUESTION_IMG_DIR_PATH,
                               question_comments=data_manager_universal.look_for_comments('comments', 'question_id',
                                                                                          question_id),
                               data_manager=data_manager_universal,
                               tags=relevant_tags,
                               logged_in=logged_in,
                               username=username
                               )
    except psycopg2.Error and KeyError and IndexError as error:
        error_code = util.find_error_code(error, pgcode=psycopg2.Error.pgcode)
        return render_template("error.html",
                               error_code=error_code,
                               logged_in=logged_in,
                               username=username)


@app.route("/add-question", methods=["GET", "POST"])
def add_question():
    logged_in = True if "username" in session else False
    if logged_in:
        username = session["username"] if logged_in else None
        if request.method == "POST":
            submission_time = str(datetime.now()).split(".")[0]
            title = request.form['title'].replace("'", "`")
            message = request.form['message'].replace("'", "`")
            active_user_id = escape(session['user_id'])
            data_manager_questions.add_new_question(submission_time=submission_time,
                                                    view_number=0,
                                                    vote_number=0,
                                                    title=title,
                                                    message=message,
                                                    active_user_id=active_user_id
                                                    )
            new_question = data_manager_questions.find_question_id(submission_time, title)
            util.handle_images({"request_files": request.files,
                                "new_id": str(new_question["id"]),
                                "directory": data_manager_universal.QUESTION_IMG_DIR_PATH,
                                "else_filename": ""}, 'questions')
            return redirect("/question/" + str(new_question["id"]) + "?voted=True")
        return render_template("add_question.html",
                               logged_in=logged_in,
                               username=username
                               )
    return redirect(url_for("login"))


@app.route("/question/<question_id>/edit_question", methods=["GET", "POST"])
def edit_question(question_id):
    logged_in = True if "username" in session else False
    if logged_in:
        username = session["username"] if logged_in else None
        target_question = data_manager_universal.find_target(question_id, 'id', 'questions')[0]
        if username == target_question["user_id"]:
            if request.method == "POST":
                util.handle_images({"request_files": request.files,
                                    "new_id": question_id,
                                    "directory": data_manager_universal.QUESTION_IMG_DIR_PATH,
                                    "else_filename": target_question['image']}, 'questions')
                title = request.form['title'].replace("'", "`")
                message = request.form['message'].replace("'", "`")
                data_manager_questions.edit_question(question_id, title, message)
                return redirect("/question/" + str(target_question['id']) + "?voted=True")
            return render_template("edit_question.html",
                                   question=target_question,
                                   logged_in=logged_in,
                                   username=username
                                   )
        return render_template("error.html", error_code='Only the author can edit this question!')
    return redirect(url_for("login"))


@app.route("/question/<question_id>/vote_up")
def vote_up_question(question_id):
    if "username" in session:
        data_manager_universal.vote(question_id, 'questions', 1)
        connected_user = data_manager_users.find_connected_user(question_id, 'questions')['user_id']
        reputation_change = data_manager_users.REPUTATION_CHANGE['q_vote_up']
        data_manager_users.change_user_reputation(connected_user, int(reputation_change))
        return redirect("/question/" + question_id + "?voted=True")
    return redirect(url_for('login'))


@app.route("/question/<question_id>/vote_down")
def vote_down_question(question_id):
    if "username" in session:
        data_manager_universal.vote(question_id, 'questions', -1)
        connected_user = data_manager_users.find_connected_user(question_id, 'questions')['user_id']
        reputation_change = data_manager_users.REPUTATION_CHANGE['q_vote_down']
        data_manager_users.change_user_reputation(connected_user, int(reputation_change))
        return redirect("/question/" + question_id + "?voted=True")
    return redirect(url_for('login'))


@app.route("/answer/<answer_id>/vote_up")
def vote_up_answer(answer_id):
    if "username" in session:
        data_manager_universal.vote(answer_id, 'answers', 1)
        question_id = data_manager_answers.find_question_id_from_answer_id(answer_id)['question_id']
        connected_user = data_manager_users.find_connected_user(answer_id, 'answers')['user_id']
        reputation_change = data_manager_users.REPUTATION_CHANGE['a_vote_up']
        data_manager_users.change_user_reputation(connected_user, int(reputation_change))
        return redirect("/question/" + str(question_id) + "?voted=True")
    return redirect(url_for('login'))


@app.route("/answer/<answer_id>/vote_down")
def vote_down_answer(answer_id):
    if "username" in session:
        data_manager_universal.vote(answer_id, 'answers', -1)
        question_id = data_manager_answers.find_question_id_from_answer_id(answer_id)['question_id']
        connected_user = data_manager_users.find_connected_user(answer_id, 'answers')['user_id']
        reputation_change = data_manager_users.REPUTATION_CHANGE['a_vote_down']
        data_manager_users.change_user_reputation(connected_user, int(reputation_change))
        return redirect("/question/" + str(question_id) + "?voted=True")
    return redirect(url_for('login'))


@app.route("/question/<question_id>/new_answer", methods=["GET", "POST"])
def add_answer(question_id):
    logged_in = True if "username" in session else False
    if logged_in:
        username = session["username"] if logged_in else None
        if request.method == "POST":
            submission_time = str(datetime.now()).split(".")[0]
            message = request.form['message'].replace("'", "`")
            active_user_id = escape(session['user_id'])
            data_manager_answers.add_new_answer(submission_time=submission_time,
                                                vote_number=0,
                                                question_id=question_id,
                                                message=message,
                                                active_user_id=active_user_id,
                                                )
            new_answer = data_manager_answers.find_answer_id(submission_time, message)
            util.handle_images({"request_files": request.files,
                                "new_id": str(new_answer["id"]),
                                "directory": data_manager_universal.ANSWER_IMG_DIR_PATH,
                                "else_filename": ""}, 'answers')
            return redirect("/question/" + question_id + "?voted=True")
        return render_template("add_answer.html",
                               question_id=question_id,
                               logged_in=logged_in,
                               username=username
                               )
    return redirect(url_for("login"))


@app.route('/question/<question_id>/delete_question')
def delete_question(question_id):
    target_answers = data_manager_answers.find_answer_by_question_id(question_id)
    target_question = data_manager_universal.find_target(question_id, 'id', 'questions')[0]
    if session["user_id"] == target_question["user_id"]:
        data_manager_comments.delete_comments("question_id", question_id)
        data_manager_tags.delete_tags(question_id)
        for answer in target_answers:
            data_manager_comments.delete_comments("answer_id", answer["id"])
            if answer['image']:
                os.remove(data_manager_universal.ANSWER_IMG_DIR_PATH + "/" + answer['image'])
        data_manager_answers.delete_answers_by_question_id(question_id)
        if target_question['image']:
            os.remove(data_manager_universal.QUESTION_IMG_DIR_PATH + "/" + target_question['image'])
        data_manager_universal.delete_from_db(question_id, 'questions')
        return redirect("/list")
    return render_template("error.html", error_code='Only the author can delete this question!')


@app.route('/answer/<answer_id>/delete_answer')
def delete_answer(answer_id):
    target_answer = data_manager_universal.find_target(answer_id, 'id', 'answers')[0]
    if session["user_id"] == target_answer["user_id"]:
        if target_answer['image']:
            os.remove(data_manager_universal.ANSWER_IMG_DIR_PATH + "/" + target_answer['image'])
        data_manager_universal.delete_from_db(answer_id, 'answers')
        return redirect("/question/" + str(target_answer['question_id']) + "?voted=True")
    return render_template("error.html", error_code='Only the author can delete this question!')


@app.route('/question/<question_id>/new_comment', methods=['GET', 'POST'])
def new_comment_to_question(question_id):
    logged_in = True if "username" in session else False
    if logged_in:
        username = session["username"] if logged_in else None
        if request.method == 'POST':
            active_user_id = escape(session['user_id'])
            submission_time = str(datetime.now()).split(".")[0]
            data_manager_comments.add_comment(question_id=question_id,
                                              answer_id='null',
                                              message=request.form['message'].replace("'", "`"),
                                              submission_time=submission_time,
                                              edited_count='null',
                                              active_user_id=active_user_id)
            return redirect("/question/" + question_id + "?voted=True")
        return render_template('add_comment.html',
                               question_id=question_id,
                               logged_in=logged_in,
                               username=username
                               )
    return redirect(url_for("login"))


@app.route("/answer/<answer_id>/new_comment", methods=["GET", "POST"])
def add_comment_to_answer(answer_id):
    logged_in = True if "username" in session else False
    if logged_in:
        username = session["username"] if logged_in else None
        q_id = data_manager_answers.find_question_id_from_answer_id(answer_id)['question_id']
        if request.method == 'POST':
            active_user_id = escape(session['user_id'])
            submission_time = str(datetime.now()).split(".")[0]
            data_manager_comments.add_comment(question_id='null',
                                              answer_id=answer_id,
                                              message=request.form["message"].replace("'", "`"),
                                              submission_time=submission_time,
                                              edited_count='null',
                                              active_user_id=active_user_id)
            return redirect("/question/" + str(q_id) + "?voted=True")
        return render_template('add_comment_answer.html',
                               answer_id=answer_id,
                               question_id=q_id,
                               logged_in=logged_in,
                               username=username
                               )
    return redirect(url_for("login"))


@app.route("/search")
def search_in_questions():
    logged_in = True if "username" in session else False
    username = session["username"] if logged_in else None
    if request.args.get("q"):
        relevant_questions = data_manager_questions.filter_questions(request.args.get("q"))
        return render_template("list_searched.html",
                               questions=relevant_questions,
                               if_reversed="asc",
                               question_headers=[" ".join(header.capitalize() for header in header.split("_"))
                                                 for header in data_manager_universal.QUESTION_HEADER],
                               logged_in=logged_in,
                               username=username
                               )


@app.route("/answer/<answer_id>/edit", methods=["GET", "POST"])
def edit_answer(answer_id):
    logged_in = True if "username" in session else False
    if logged_in:
        username = session["username"] if logged_in else None
        target_answer = data_manager_universal.find_target(answer_id, 'id', 'answers')[0]
        if request.method == "POST":

            util.handle_images({"request_files": request.files,
                                "new_id": str(target_answer["id"]),
                                "directory": data_manager_universal.ANSWER_IMG_DIR_PATH,
                                "else_filename": target_answer["image"]}, 'answers')
            message = request.form['message'].replace("'", "`")
            data_manager_answers.edit_answer(answer_id, message)
            return redirect("/question/" + str(target_answer['question_id']) + "?voted=True")
        return render_template("edit_answer.html",
                               a_or_c=target_answer,
                               logged_in=logged_in,
                               username=username)
    return redirect(url_for("login"))


@app.route("/comment/<comment_id>/edit", methods=["GET", "POST"])
def edit_comment(comment_id):
    logged_in = True if "username" in session else False
    if logged_in:
        username = session["username"] if logged_in else None
        target_comment = data_manager_comments.find_comment(comment_id)[0]
        if request.method == "POST":
            data_manager_comments.update_edited_count(comment_id)
            message = request.form['message'].replace("'", "`")
            data_manager_comments.edit_comment(comment_id, message)
            return util.redirect_after_comment_action(target_comment)
        return render_template("edit_comment.html",
                               a_or_c=target_comment,
                               logged_in=logged_in,
                               username=username)
    return redirect(url_for("login"))


@app.route("/comment/<comment_id>/delete")
def delete_comment(comment_id):
    target_comment = data_manager_comments.find_comment(comment_id)[0]
    data_manager_universal.delete_from_db(comment_id, 'comments')
    return util.redirect_after_comment_action(target_comment)


@app.route("/question/<question_id>/new_tag", methods=["GET", "POST"])
def add_tag(question_id):
    if request.method == "POST":
        try:
            if request.form['message']:
                data_manager_tags.add_new_tag(request.form['message'].replace("'", "`"))
                target_tag = data_manager_tags.find_tag_id(request.form['message'].replace("'", "`"))['id']
            else:
                target_tag = data_manager_tags.find_tag_id(request.form['tag-name'])['id']
            data_manager_tags.choose_tag(question_id, target_tag)
            return redirect("/question/" + question_id + "?voted=True")
        except psycopg2.Error as error:
            return render_template("error.html", error_code=error.pgcode)
    all_tags = data_manager_tags.all_tags()
    return render_template("add_tag.html", all_tags=all_tags, question_id=question_id)


@app.route("/question/<question_id>/tag/<tag_id>/delete")
def delete_tag(question_id, tag_id):
    data_manager_tags.delete_tag(question_id, tag_id)
    return redirect("/question/" + question_id + "?voted=True")


@app.route("/sign-up", methods=["GET", "POST"])
def registration():
    if 'username' not in session:
        if request.method == "POST":
            user_emails, user_names = [email["email"] for email in data_manager_users.get_user_info('email')], \
                                [username["username"] for username in data_manager_users.get_user_info('username')]
            if request.form['email'] not in user_emails and request.form['username'] not in user_names:
                data_manager_users.add_new_user({'email': request.form["email"].replace("'", "`"),
                                                 'password': util.hash_password(
                                                     request.form["password"].replace("'", "`")),
                                                 'username': request.form["username"].replace("'", "`"),
                                                 'reputation': 0,
                                                 'image': 'null',
                                                 'registration_date': str(datetime.now()).split(".")[0]}
                                                )
                new_profile = data_manager_users.find_profile_id(request.form["email"].replace("'", "`"), 'email')
                util.handle_images({"request_files": request.files,
                                    "new_id": str(new_profile["id"]),
                                    "directory": data_manager_universal.PROFILE_IMG_DIR_PATH,
                                    "else_filename": ""}, 'users')
                return redirect("/user/" + str(new_profile["id"]))
            return render_template("error.html", error_code='Email address or user name already in use!')
        return render_template("sign_up.html")
    return render_template("error.html",
                           error_code='You are already signed up and logged in!',
                           logged_in=True,
                           username=session["username"])


@app.route("/user/<user_id>")
def profile_page(user_id):
    logged_in = True if "username" in session else False
    username = session["username"] if logged_in else None
    target_profile = data_manager_universal.find_target(user_id, "id", "users")[0]
    comments_of_user = [comment for comment in data_manager_universal.find_target(user_id, 'user_id', 'comments')]
    user_comments = []
    for comment in comments_of_user:
        if comment["answer_id"]:
            comment["question_id"] = data_manager_answers.find_question_id_from_answer_id(
                comment["answer_id"])["question_id"]
        user_comments.append(comment)
    return render_template("profile_page.html",
                           user=target_profile,
                           logged_in=logged_in,
                           answer_count=data_manager_universal.execute_count('answers', 'user_id', user_id)['count'],
                           answer_headers=[" ".join(header.capitalize() for header in header.split("_"))
                                           for header in data_manager_universal.ANSWER_HEADER],
                           comment_count=data_manager_universal.execute_count('comments', 'user_id', user_id)['count'],
                           comment_headers=[" ".join(header.capitalize() for header in header.split("_"))
                                            for header in data_manager_universal.COMMENT_HEADER],
                           question_count=data_manager_universal.execute_count('questions', 'user_id', user_id)['count'],
                           question_headers=[" ".join(header.capitalize() for header in header.split("_"))
                                             for header in data_manager_universal.QUESTION_HEADER],
                           user_questions=[question for question in data_manager_universal.find_target(
                               user_id, 'user_id', 'questions')],
                           user_answers=[answer for answer in data_manager_universal.find_target(
                               user_id, 'user_id', 'answers')],
                           user_comments=user_comments,
                           username=username
                           )


@app.route("/users")
def users():
    logged_in = True if "username" in session else False
    username = session["username"] if logged_in else None
    if request.args.get("order_by") and request.args.get("order_direction") == "desc":
        sorted_users = data_manager_users.get_ordered_users(request.args.get("order_by"), 'DESC')
        order = "asc"
    elif request.args.get("order_by") and request.args.get("order_direction") == "asc":
        sorted_users = data_manager_users.get_ordered_users(request.args.get("order_by"), 'ASC')
        order = "desc"
    else:
        order = "asc"
        sorted_users = data_manager_users.get_ordered_users("username", 'DESC')
    return render_template("list_users.html",
                           users=sorted_users,
                           if_reversed=order,
                           user_headers=[" ".join(header.capitalize() for header in header.split("_"))
                                         for header in data_manager_universal.USER_HEADER],
                           logged_in=logged_in,
                           username=username
                           )


@app.route("/login", methods=["GET", "POST"])
def login():
    logged_in = True if "username" in session else False
    if not logged_in:
        if request.method == 'POST':
            email = request.form['email'].replace("'", "`")
            password = request.form['password'].replace("'", "`")
            user_emails = [email["email"] for email in data_manager_users.get_user_info('email')]
            username = data_manager_users.find_user_name(email)['username']
            user_password = data_manager_users.find_user_password(email)['password']
            verified = util.verify_password(password, user_password)
            if email not in user_emails or not verified:
                return render_template('login.html', verified=verified)
            else:
                session['username'] = username
                session['user_id'] = data_manager_users.find_profile_id(email, 'email')['id']
                return redirect("/")
        return render_template("login.html",
                               verified=True,
                               logged_in=logged_in)
    return render_template("error.html",
                           error_code='You are already signed up and logged in!',
                           logged_in=logged_in,
                           username=session["username"] if logged_in else None)


@app.route('/tags')
def tags():
    logged_in = True if "username" in session else False
    username = session["username"] if logged_in else None
    if request.args.get("order_by") and request.args.get("order_direction") == "desc":
        sorted_tags = data_manager_tags.get_ordered_tags(request.args.get("order_by"), 'DESC')
        order = "asc"
    elif request.args.get("order_by") and request.args.get("order_direction") == "asc":
        sorted_tags = data_manager_tags.get_ordered_tags(request.args.get("order_by"), 'ASC')
        order = "desc"
    else:
        order = "asc"
        sorted_tags = data_manager_tags.get_ordered_tags('used', 'DESC')
    return render_template("list_tags.html",
                           tags=sorted_tags,
                           if_reversed=order,
                           tag_headers=[" ".join(header.capitalize() for header in header.split("_"))
                                        for header in data_manager_universal.TAG_HEADER],
                           logged_in=logged_in,
                           username=username
                           )
    pass


@app.route('/logout')
def logout():
    for credential in ["username", "user_id"]:
        session.pop(credential, None)
    return redirect(url_for('login'))


@app.route('/question/<question_id>/accept_answer', methods=['GET', 'POST'])
def accept_answer(question_id):
    if request.method == 'POST':
        accepted = ('accepted' == request.form['accept'])
        answer_id = request.form.get('answer-id', type=int)
        data_manager_answers.update_accept_answer(answer_id, accepted)
        return redirect(request.referrer)


if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )
