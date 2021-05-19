import database_common


@database_common.connection_handler
def find_answers_to_question(cursor, question_id):
    query = """
            SELECT * FROM answers
            WHERE question_id = '%s'
            ORDER BY vote_number;""" % question_id
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def find_question_id_from_answer_id(cursor, answer_id):
    query = """
            SELECT question_id FROM answers
            WHERE id = '%s'
            """ % answer_id
    cursor.execute(query)
    return cursor.fetchone()


@database_common.connection_handler
def find_answer_id(cursor, submission_time, message):
    query = """
            SELECT id FROM answers
            WHERE submission_time = '%s'
            AND message = '%s'""" % (submission_time, message)
    cursor.execute(query)
    return cursor.fetchone()


@database_common.connection_handler
def add_new_answer(
        cursor, submission_time, vote_number, question_id, message, active_user_id):
    query = """
            INSERT INTO answers
            (submission_time, vote_number, question_id, message, user_id)
            VALUES ('%s', %s, %s, '%s', '%s');""" % (submission_time, vote_number, question_id, message, active_user_id)
    cursor.execute(query)


@database_common.connection_handler
def find_answer_by_question_id(cursor, question_id):
    query = """
            SELECT * FROM answers
            WHERE question_id = '%s';
            """ % question_id
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def delete_answers_by_question_id(cursor, question_id):
    query = """
            DELETE FROM answers
            WHERE question_id = '%s';
            """ % question_id
    cursor.execute(query)


@database_common.connection_handler
def edit_answer(cursor, answer_id, message):
    query = """
            UPDATE answers 
            SET message = '%s'
            WHERE id = '%s'""" % (message, answer_id)
    cursor.execute(query)


@database_common.connection_handler
def update_accept_answer(cursor, answer_id, accepted):
    query = """
            UPDATE answers 
            SET accepted = '%s'
            WHERE id = '%s'""" % (accepted, answer_id)
    cursor.execute(query)
