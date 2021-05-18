import os
import data_manager


def save_images(form, id_type, dir_path):
    filename = id_type + "." + "".join(form['image'].filename.split(".")[1])
    form['image'].save(os.path.join(dir_path, filename))
    return filename


def handle_images(update_info, data_table):
    if update_info["request_files"]['image']:
        filename = save_images(update_info["request_files"],
                               update_info["new_id"],
                               update_info["directory"]
                               )
    else:
        filename = update_info["else_filename"]
    data_manager_universal.update_image(filename,
                                        update_info["new_id"],
                                        data_table)
