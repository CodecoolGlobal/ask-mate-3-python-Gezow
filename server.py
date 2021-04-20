from flask import Flask, render_template, redirect
import connection
import data_manager


app = Flask(__name__)
questions = connection.get_all_user_data(data_manager.QUESTION_FILE_PATH)
question_headers = data_manager.QUESTION_HEADER


@app.route("/")
def main():
    return render_template("list.html",
                           questions=questions,
                           question_headers=[" ".join(header.capitalize() for header in header.split("_")) for header in question_headers]
                           )


if __name__ == "__main__":
    app.run()
