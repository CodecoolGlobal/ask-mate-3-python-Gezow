import database_common


@database_common.connection_handler
def get_ordered_questions(cursor, filter_type, order):
    query = """
            SELECT * FROM question
            ORDER BY %s %s;""" % (filter_type, order)
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
def edit_question(cursor, question_id, title, message):
    query = """
            UPDATE question 
            SET title = '%s', message = '%s'
            WHERE id = '%s'""" % (title, message, question_id)
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
