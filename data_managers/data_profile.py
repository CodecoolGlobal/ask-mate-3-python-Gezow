import database_common


REPUTATION_CHANGE = {"q_vote_up": 5, "a_vote_up": 10, "a_accepted": 15, "q_vote_down": -2, "a_vote_down": -2}


@database_common.connection_handler
def get_user_info(cursor, aspect):
    cursor.execute("SELECT %s FROM profile;" % aspect)
    return cursor.fetchall()


@database_common.connection_handler
def add_new_user(cursor, parameters):
    query = """INSERT INTO profile (email, password, username, reputation, image, registration_date)
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
    query = """SELECT id FROM profile
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
                    (select count(*) from question where user_id=profile.id) as question_count,
                    (select count(*) from answer where user_id=profile.id) as answer_count,
                    (select count(*) from comment where user_id=profile.id) as comment_count,
                    image,
                    registration_date
            FROM profile
            ORDER BY %s %s;""" % (filter_type, order)
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def find_user_password(cursor, email):
    query = """
            SELECT password FROM profile
            WHERE email = '%s';""" % email
    cursor.execute(query)
    return cursor.fetchone()


@database_common.connection_handler
def find_user_name(cursor, email):
    query = """
            SELECT username FROM profile
            WHERE email = '%s';""" % email
    cursor.execute(query)
    return cursor.fetchone()


@database_common.connection_handler
def change_user_reputation(cursor, selected_user, number):
    query = """
            UPDATE profile
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

