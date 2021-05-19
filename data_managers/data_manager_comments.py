import database_common


@database_common.connection_handler
def add_comment(cursor, question_id, answer_id, message, submission_time, edited_count, active_user_id):
    query = """
            INSERT INTO comments
            (question_id, answer_id, message, submission_time, edited_count, user_id)
            VALUES (%s, %s, '%s','%s',%s, '%s');
            """ % (question_id, answer_id, message, submission_time, edited_count, active_user_id)
    cursor.execute(query)


@database_common.connection_handler
def find_comment(cursor, comment_id):
    query = """
            SELECT * FROM comments
            WHERE id = '%s'
            """ % comment_id
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def edit_comment(cursor, comment_id, message):
    query = """
            UPDATE comments 
            SET message = '%s'
            WHERE id = '%s'""" % (message, comment_id)
    cursor.execute(query)


@database_common.connection_handler
def update_edited_count(cursor, comment_id):
    query = """
            UPDATE comments
            SET edited_count = CASE WHEN edited_count IS null THEN 1 ELSE edited_count + 1 END
            WHERE id = '%s'""" % comment_id
    cursor.execute(query)
