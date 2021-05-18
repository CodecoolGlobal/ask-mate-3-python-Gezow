import database_common


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
