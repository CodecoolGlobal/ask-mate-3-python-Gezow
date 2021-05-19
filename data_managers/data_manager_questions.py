import database_common


@database_common.connection_handler
def get_ordered_questions(cursor, filter_type, order):
    query = """
            SELECT * FROM questions
            ORDER BY %s %s;""" % (filter_type, order)
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def update_view_number(cursor, question_id):
    query = """
            UPDATE questions
            SET view_number = view_number + 1
            WHERE id = '%s';""" % question_id
    cursor.execute(query)


@database_common.connection_handler
def add_new_question(cursor, submission_time, view_number, vote_number, title, message, active_user_id):
    query = """
            INSERT INTO questions
            (submission_time, view_number, vote_number, title, message, user_id)
            VALUES ('%s', %s, %s, '%s', '%s', '%s');""" % (submission_time, view_number,
                                                           vote_number, title, message, active_user_id)
    cursor.execute(query)


@database_common.connection_handler
def find_question_id(cursor, submission_time, title):
    query = """
            SELECT id FROM questions
            WHERE submission_time = '%s'
            AND title = '%s'""" % (submission_time, title)
    cursor.execute(query)
    return cursor.fetchone()


@database_common.connection_handler
def edit_question(cursor, question_id, title, message):
    query = """
            UPDATE questions 
            SET title = '%s', message = '%s'
            WHERE id = '%s'""" % (title, message, question_id)
    cursor.execute(query)


@database_common.connection_handler
def filter_questions(cursor, search_field_text):
    query = """
            SELECT questions.id, questions.submission_time, questions.view_number, questions.vote_number, questions.title,
            questions.message, questions.image, questions.user_id
            FROM questions
            JOIN answers ON questions.id = answers.question_id
            WHERE questions.message ILIKE '%s'
            OR questions.title ILIKE '%s'
            OR answers.message ILIKE '%s'
            GROUP BY questions.id;""" % ('%' + search_field_text + '%',
                                        '%' + search_field_text + '%',
                                        '%' + search_field_text + '%'
                                        )
    cursor.execute(query)
    return cursor.fetchall()
