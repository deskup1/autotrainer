from transformers import pipeline
import glob
import shutil
import os.path
import difPy
import os


similarity_treshold = 'similar'
imdir = 'images'
duplicate_images_dir = 'duplicates'

ext = ['png', 'jpg', 'bmp']

if __name__ == '__main__':
    dif = difPy.build([os.curdir + "/" + imdir])
    search = difPy.search(dif, similarity=similarity_treshold)
    for image in search.lower_quality["lower_quality"]:
        shutil.move(image, image.replace(imdir, duplicate_images_dir))
        caret = image.rsplit(".", 1)[0] + ".txt"
        if os.path.isfile(caret):
            shutil.move(caret, caret.replace(imdir, duplicate_images_dir))

