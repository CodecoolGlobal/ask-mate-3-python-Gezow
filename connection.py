import csv
import random
import string


def append_data(database, data_to_append):
    database.append(data_to_append)

def write_data_in_file(file_name, user_data, DATA_HEADER, separator=","):
    with open(file_name, "w") as data_file:
        writer = csv.DictWriter(data_file, fieldnames=DATA_HEADER)
        data_file.write(separator.join(DATA_HEADER) + "\n")
        for data in user_data:
            writer.writerow(data)


def get_all_user_data(DATA_FILE_PATH):
    with open(DATA_FILE_PATH) as datas:
        return [data for data in csv.DictReader(datas)]


def generate_id(number_of_small_letters=2,
                number_of_capital_letters=2,
                number_of_digits=1,
                number_of_special_chars=1,
                allowed_special_chars=r"_+-!"):
    abc_upper = list(string.ascii_uppercase)
    abc_lower = list(string.ascii_lowercase)
    digits = list(string.digits)
    spec_chars = ['_', '+', '-', '!']
    generated_id = ''
    for small_letters in range(number_of_small_letters):
        generated_id += random.choice(abc_lower)
    for capital_letters in range(number_of_capital_letters):
        generated_id += random.choice(abc_upper)
    for number in range(number_of_digits):
        generated_id += random.choice(digits)
    for char in range(number_of_special_chars):
        generated_id += random.choice(spec_chars)
    unique_id = ''.join(random.sample(generated_id, len(generated_id)))
    return unique_id





