import os
import database_common


Q_IMAGE_DIR_PATH = os.getenv('Q_IMAGE_DIR_PATH') if 'Q_IMAGE_DIR_PATH' in os.environ else './static/images/question'
A_IMAGE_DIR_PATH = os.getenv('A_IMAGE_DIR_PATH') if 'A_IMAGE_DIR_PATH' in os.environ else './static/images/answer'
QUESTION_HEADER = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
ANSWER_HEADER = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']


@database_common.connection_handler
def get_ordered_questions(cursor, filter_type, order):
    query = """
            SELECT * FROM question
            ORDER BY %s %s;""" % (filter_type, order)
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def find_target(cursor, question_id, db):
    query = """
            SELECT * FROM %s
            WHERE id = '%s';""" % (db, question_id)
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def update_view_number(cursor, question_id):
    query = """
            UPDATE question
            SET view_number = view_number + 1
            WHERE id = '%s';""" % question_id
    cursor.execute(query)


@database_common.connection_handler
def find_answers_to_question(cursor, question_id):
    query = """
            SELECT * FROM answer
            WHERE question_id = '%s'
            ORDER BY vote_number;""" % question_id
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def add_new_question(cursor, submission_time, view_number, vote_number, title, message):
    query = """
            INSERT INTO question
            (submission_time, view_number, vote_number, title, message)
            VALUES ('%s', %s, %s, '%s', '%s');""" % (submission_time,
                                                     view_number,
                                                     vote_number,
                                                     title,
                                                     message
                                                     )
    cursor.execute(query)


@database_common.connection_handler
def find_question_id(cursor, submission_time, title):
    query = """
            SELECT id FROM question
            WHERE submission_time = '%s'
            AND title = '%s'""" % (submission_time, title)
    cursor.execute(query)
    return cursor.fetchone()


@database_common.connection_handler
def update_image(cursor, filename, unique_id, db):
    query = """
            UPDATE %s 
            SET image = '%s'
            WHERE id = '%s';""" % (db, filename, unique_id)
    cursor.execute(query)


@database_common.connection_handler
def edit_question(cursor, question_id, title, message):
    query = """
            UPDATE question 
            SET title = '%s', message = '%s'
            WHERE id = '%s'""" % (title, message, question_id)
    cursor.execute(query)


@database_common.connection_handler
def vote(cursor, id, db, up_or_down):
    query = """
            UPDATE %s
            SET vote_number = vote_number + %s
            WHERE id = '%s'
            """ % (db, up_or_down, id)
    cursor.execute(query)


@database_common.connection_handler
def find_question_id_from_answer_id(cursor, answer_id):
    query = """
            SELECT question_id FROM answer
            WHERE id = '%s'
            """ % answer_id
    cursor.execute(query)
    return cursor.fetchone()


@database_common.connection_handler
def find_answer_id(cursor, submission_time, message):
    query = """
            SELECT id FROM answer
            WHERE submission_time = '%s'
            AND message = '%s'""" % (submission_time, message)
    cursor.execute(query)
    return cursor.fetchone()


@database_common.connection_handler
def add_new_answer(
        cursor, submission_time, vote_number, question_id, message):
    query = """
            INSERT INTO answer
            (submission_time, vote_number, question_id, message)
            VALUES ('%s', %s, %s, '%s');""" % (submission_time, vote_number, question_id, message)
    cursor.execute(query)


@database_common.connection_handler
def delete_from_db(cursor, unique_id, db):
    query = """
            DELETE FROM %s
            WHERE id = '%s';
            """ % (db, unique_id)
    cursor.execute(query)


@database_common.connection_handler
def look_for_comments(cursor, db, id_type, unique_id):
    query = """
            SELECT * FROM %s
            WHERE %s = '%s'
            ORDER BY submission_time;
            """ % (db, id_type, unique_id)
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def find_answer_by_question_id(cursor, question_id):
    query = """
            SELECT * FROM answer
            WHERE question_id = '%s';
            """ % question_id
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def delete_answers_by_question_id(cursor, question_id):
    query = """
            DELETE FROM answer
            WHERE question_id = '%s';
            """ % question_id
    cursor.execute(query)


@database_common.connection_handler
def add_comment(cursor, question_id, answer_id, message, submission_time, edited_count):
    query = """
            INSERT INTO comment
            (question_id, answer_id, message, submission_time, edited_count)
            VALUES (%s, %s, '%s','%s',%s);
            """ % (question_id, answer_id, message, submission_time, edited_count)
    cursor.execute(query)


@database_common.connection_handler
def filter_questions(cursor, search_field_text):
    query = """
            SELECT question.id, question.submission_time, view_number, question.vote_number, question.title,
            question.message, question.image
            FROM question
            FULL OUTER JOIN answer ON question.id = answer.question_id
            WHERE question.message ILIKE '%s'
            OR question.title ILIKE '%s'
            OR answer.message ILIKE '%s';""" % ('%' + search_field_text + '%',
                                                '%' + search_field_text + '%',
                                                '%' + search_field_text + '%'
                                                )
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def edit_answer(cursor, answer_id, message):
    query = """
            UPDATE answer 
            SET message = '%s'
            WHERE id = '%s'""" % (message, answer_id)
    cursor.execute(query)
