import os

file_names = ['original', 'modified']
image_types = ['jpg', 'jpeg', 'png']


def remove_created_files():
    for s in file_names:
        for t in image_types:
            if os.path.exists(s + '.' + t):
                os.remove(s + '.' + t)
