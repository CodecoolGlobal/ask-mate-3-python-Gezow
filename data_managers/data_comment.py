import database_common


@database_common.connection_handler
def add_comment(cursor, question_id, answer_id, message, submission_time, edited_count, active_user_id):
    query = """
            INSERT INTO comment
            (question_id, answer_id, message, submission_time, edited_count, user_id)
            VALUES (%s, %s, '%s','%s',%s, '%s');
            """ % (question_id, answer_id, message, submission_time, edited_count, active_user_id)
    cursor.execute(query)


@database_common.connection_handler
def find_comment(cursor, comment_id):
    query = """
            SELECT * FROM comment
            WHERE id = '%s'
            """ % comment_id
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def edit_comment(cursor, comment_id, message):
    query = """
            UPDATE comment 
            SET message = '%s'
            WHERE id = '%s'""" % (message, comment_id)
    cursor.execute(query)


@database_common.connection_handler
def update_edited_count(cursor, comment_id):
    query = """
            UPDATE comment
            SET edited_count = CASE WHEN edited_count IS null THEN 1 ELSE edited_count + 1 END
            WHERE id = '%s'""" % comment_id
    cursor.execute(query)


@database_common.connection_handler
def delete_comments(cursor, delete_by, equals_to):
    query = """DELETE FROM comment
            WHERE %s = '%s';""" % (delete_by, equals_to)
    cursor.execute(query)
