import database_common


@database_common.connection_handler
def get_ordered_users(cursor, filter_type, order):
    query = """
            SELECT id, username, email, reputation, image FROM users
            ORDER BY %s %s;""" % (filter_type, order)
    cursor.execute(query)
    return cursor.fetchall()

