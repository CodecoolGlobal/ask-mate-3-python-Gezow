from flask import redirect
import os
import data_manager_universal
import data_manager_answer
import bcrypt


def hash_password(plain_text_password):
    hashed_bytes = bcrypt.hashpw(plain_text_password.encode('utf-8'), bcrypt.gensalt())
    return hashed_bytes.decode('utf-8')


def verify_password(plain_text_password, hashed_password):
    hashed_bytes_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_bytes_password)


def save_images(form, id_type, dir_path):
    image = form['image']
    filename = id_type + "." + "".join(image.filename.split(".")[1])
    image.save(os.path.join(dir_path, filename))
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


def redirect_after_comment_action(target_comment):
    if target_comment['question_id']:
        return redirect(f"/question/{str(target_comment['question_id'])}?voted=True")
    if target_comment['answer_id']:
        target_question_id = data_manager_answer.find_question_id_from_answer_id(
            target_comment['answer_id'])["question_id"]
        return redirect(f"/question/{str(target_question_id)}?voted=True")
