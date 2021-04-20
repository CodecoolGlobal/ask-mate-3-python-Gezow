import csv


def append_data(database, data_to_append):
    database.append(data_to_append)


def write_data_in_file(file_name, user_data, DATA_HEADER, separator=","):
    with open(file_name, "w") as data_file:
        writer = csv.DictWriter(data_file, fieldnames=DATA_HEADER)
        data_file.write(separator.join(DATA_HEADER) + "\n")
        for data in user_data:
            writer.writerow(data)


def get_all_user_data(DATA_FILE_PATH):
    with open(DATA_FILE_PATH) as infos:
        return [data for data in csv.DictReader(infos)]
