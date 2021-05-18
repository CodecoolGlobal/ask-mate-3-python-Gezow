import database_common


@database_common.connection_handler
def get_user_info(cursor, aspect):
    cursor.execute("SELECT %s FROM users;" % aspect)
    return cursor.fetchall()


@database_common.connection_handler
def add_new_user(cursor, parameters):
    query = """INSERT INTO users (email, password, username, reputation, image, registration_date)
            VALUES('%s', '%s', '%s', %s, '%s', '%s');""" % (parameters["email"],
                                                            parameters["password"],
                                                            parameters["username"],
                                                            parameters["reputation"],
                                                            parameters["image"],
                                                            parameters["registration_date"]
                                                            )
    cursor.execute(query)


@database_common.connection_handler
def find_profile_id(cursor, search_parameter, parameter_type):
    query = """SELECT id FROM users
            WHERE %s = '%s';""" % (parameter_type, search_parameter)
    cursor.execute(query)
    return cursor.fetchone()


@database_common.connection_handler
def get_ordered_users(cursor, filter_type, order):
    query = """
            SELECT id, username, email, reputation, image, registration_date FROM users
            ORDER BY %s %s;""" % (filter_type, order)
    cursor.execute(query)
    return cursor.fetchall()
