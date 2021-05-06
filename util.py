import os


def save_images(form, id_type, dir_path):
    print(form, id_type, dir_path)
    image = form['image']
    filename = id_type + "." + "".join(image.filename.split(".")[1])
    print(os.path.join(dir_path, filename))
    image.save(os.path.join(dir_path, filename))
    return filename
