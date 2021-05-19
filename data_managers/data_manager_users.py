import database_common


REPUTATION_CHANGE = {"q_vote_up": 5, "a_vote_up": 10, "a_accepted": 15, "q_vote_down": -2, "a_vote_down": -2}


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
            SELECT  id,
                    username,
                    email,
                    reputation,
                    (select count(*) from questions where user_id=users.id) as question_count,
                    (select count(*) from answers where user_id=users.id) as answer_count,
                    (select count(*) from comments where user_id=users.id) as comment_count,
                    image,
                    registration_date
            FROM users
            ORDER BY %s %s;""" % (filter_type, order)
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def find_user_password(cursor, email):
    query = """
            SELECT password FROM users
            WHERE email = '%s';""" % email
    cursor.execute(query)
    return cursor.fetchone()


@database_common.connection_handler
def find_user_name(cursor, email):
    query = """
            SELECT username FROM users
            WHERE email = '%s';""" % email
    cursor.execute(query)
    return cursor.fetchone()


@database_common.connection_handler
def change_user_reputation(cursor, selected_user, number):
    query = """
            UPDATE users
            SET reputation = reputation + '%d'
            WHERE id = '%s';""" % (number, selected_user)
    cursor.execute(query)


@database_common.connection_handler
def find_connected_user(cursor, object_id, target_table):
    query = """
            SELECT user_id FROM %s
            WHERE id = '%s';""" % (target_table, object_id)
    cursor.execute(query)
    return cursor.fetchone()

