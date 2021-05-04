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
