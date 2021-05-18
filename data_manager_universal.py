import os
import database_common


QUESTION_IMG_DIR_PATH = os.getenv('QUESTION_IMG_DIR_PATH') \
    if 'QUESTION_IMG_DIR_PATH' in os.environ else './static/images/question'
ANSWER_IMG_DIR_PATH = os.getenv('ANSWER_IMG_DIR_PATH') \
    if 'ANSWER_IMG_DIR_PATH' in os.environ else './static/images/answer'
PROFILE_IMG_DIR_PATH = os.getenv('PROFILE_IMG_DIR_PATH') \
    if 'PROFILE_IMG_DIR_PATH' in os.environ else './static/images/profile'
QUESTION_HEADER = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image', 'user_id']
ANSWER_HEADER = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image', 'user_id']
USER_HEADER = ['id', 'username', 'email', 'reputation', 'image', 'registration_date']


@database_common.connection_handler
def find_target(cursor, unique_id, search_aspect, db):
    query = """
            SELECT * FROM %s
            WHERE %s = '%s';""" % (db, search_aspect, unique_id)
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def update_image(cursor, filename, unique_id, db):
    query = """
            UPDATE %s 
            SET image = '%s'
            WHERE id = '%s';""" % (db, filename, unique_id)
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
def execute_count(cursor, table, search_aspect, search_text):
    query = """SELECT COUNT(*) FROM %s
            WHERE %s = '%s'""" % (table, search_aspect, search_text)
    cursor.execute(query)
    return cursor.fetchone()
