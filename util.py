import os
import data_manager


def save_images(form, id_type, dir_path):
    filename = id_type + "." + "".join(form['image'].filename.split(".")[1])
    form['image'].save(os.path.join(dir_path, filename))
    return filename


def handle_images(request_files, new_profile_id):
    if request_files['image']:
        filename = save_images(request_files, new_profile_id,  data_manager.PROFILE_PICTURE_IMAGE_DIR_PATH)
    else:
        filename = ""
    return filename
