import os
import database_common


QUESTION_FILE_PATH = os.getenv(
    'QUESTION_FILE_PATH') if 'QUESTION_FILE_PATH' in os.environ else 'sample_data/question.csv'
IMAGE_DIR_PATH = os.getenv('IMAGE_DIR_PATH') if 'IMAGE_DIR_PATH' in os.environ else 'static/images'
QUESTION_HEADER = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
ANSWER_FILE_PATH = os.getenv('ANSWER_FILE_PATH') if 'ANSWER_FILE_PATH' in os.environ else 'sample_data/answer.csv'
ANSWER_HEADER = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']


# from typing import List, Dict
# from psycopg2 import sql


@database_common.connection_handler
def get_questions(cursor):
    query = """
            SELECT * FROM question
            ORDER BY submission_time;"""
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_ordered_questions_desc(cursor, filter_type):
    query = """
            SELECT * FROM question
            ORDER BY %s DESC;""" % filter_type
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_ordered_questions_asc(cursor, filter_type):
    query = """
            SELECT * FROM question
            ORDER BY %s;""" % filter_type
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def find_target_question(cursor, question_id):
    query = """
            SELECT * FROM question
            WHERE id = '%s';""" % question_id
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
def add_new_question(
        cursor, submission_time, view_number, vote_number, title, message):
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
def find_id(cursor, submission_time, title):
    query2 = """
            SELECT id FROM question
            WHERE submission_time = '%s'
            AND title = '%s'""" % (submission_time, title)
    cursor.execute(query2)
    return cursor.fetchone()


@database_common.connection_handler
def update_image(cursor, filename, unique_id):
    query = """
            UPDATE question 
            SET image = '%s'
            WHERE id = '%s';""" % (filename, unique_id)
    cursor.execute(query)
