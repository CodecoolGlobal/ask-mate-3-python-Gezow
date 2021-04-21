import random
import string
import os
import data_manager


# Function to generate ids for new questions or answers:
def generate_id(
        number_of_small_letters=4,
        number_of_capital_letters=2,
        number_of_digits=4,
        ):
    characters = []
    # Calling 'add_characters()' function for each argument.
    add_characters(string.ascii_lowercase, number_of_small_letters, characters)
    add_characters(string.ascii_uppercase,
                   number_of_capital_letters, characters)
    add_characters("0123456789", number_of_digits, characters)
    # Shuffle the output list
    random.shuffle(characters)
    # Return output list as one string.
    return ''.join(characters)


# Supporting function of generate_id(...), add characters to output
# as requested by it's caller.
def add_characters(pool, aspect, characters):
    for addition in range(aspect):
        characters.append(random.choice(pool))


# Setting up dictionaries!
def setting_up_dict(ques_or_answ, id_type, submission_time, view_or_vote_number, image_input, question_id, data_header,
                    form):
    for header in data_header:
        if header == "id":
            ques_or_answ[header] = id_type
        elif header == "submission_time":
            ques_or_answ[header] = submission_time
        elif header == "view_number" or header == "vote_number":
            ques_or_answ[header] = view_or_vote_number
        elif header == "image":
            ques_or_answ[header] = image_input
        elif header == "question_id":
            ques_or_answ[header] = question_id
        else:
            ques_or_answ[header] = form[header]


# Generates a list of objects that possess the value (or unique id) we are searching for.
def generate_lst_of_targets(unique_list, unique_id, search_for):
    return [que_or_ans for que_or_ans in unique_list if que_or_ans[search_for] == unique_id]


def save_images(form, id_type):
    image = form['image']
    filename = id_type + "." + "".join(image.filename.split(".")[1])
    image.save(os.path.join(data_manager.IMAGE_DIR_PATH, filename))
    return filename
