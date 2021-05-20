import database_common


@database_common.connection_handler
def find_relevant_tags(cursor, question_id):
    query = """
            SELECT * FROM tag
            JOIN question_tag ON tag.id = question_tag.tag_id
            WHERE question_tag.question_id = '%s';
            """ % question_id
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def all_tags(cursor):
    query = """
            SELECT tag.name FROM tag
            """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def add_new_tag(cursor, tag):
    query = """
            INSERT INTO tag
            (name) VALUES ('%s')
            """ % tag
    cursor.execute(query)


@database_common.connection_handler
def choose_tag(cursor, question_id, tag):
    query = """
            INSERT INTO question_tag
            (question_id, tag_id) VALUES ('%s','%s')
            """ % (question_id, tag)
    cursor.execute(query)


@database_common.connection_handler
def find_tag_id(cursor, tag_name):
    query = """
            SELECT id FROM tag
            WHERE name = '%s'
            """ % tag_name
    cursor.execute(query)
    return cursor.fetchone()


@database_common.connection_handler
def delete_tag(cursor, question_id, tag_id):
    query = """
            DELETE FROM question_tag
            WHERE question_id = '%s' 
            AND tag_id = '%s'
            """ % (question_id, tag_id)
    cursor.execute(query)


@database_common.connection_handler
def get_ordered_tags(cursor, filter_type, order):
    query = """
            SELECT name, (select count(*) from question_tag where tag.id = question_tag.tag_id) as used
            FROM tag
            ORDER BY %s %s;""" % (filter_type, order)
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def delete_tags(cursor, question_id):
    query = """
                DELETE FROM question_tag
                WHERE question_id = '%s';
                """ % question_id
    cursor.execute(query)
