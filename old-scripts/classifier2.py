import glob
import shutil
import os.path
import utils
import os

treshold = 0.93

imdir = 'images'
bad_images_dir = 'bad'
good_images_dir = 'good'

ext = ['png', 'jpg', 'bmp']

if __name__ == '__main__':

    images = []
    [images.extend(glob.glob( os.curdir + "/" + imdir + '/*.' + e)) for e in ext]
    print("images: " + str(len(images)))

    for id, image in enumerate(images):
        score = utils.classifier2(image, treshold, bad_images_dir)
        print(str(id+1) + "/" + str(len(images)) + " : " + str(score) + " - " + image)

        caret = image.rsplit(".", 1)[0] + ".txt"
        if os.path.isfile(image):
            shutil.move(image,  os.path.join(good_images_dir, os.path.basename(image)))
            if os.path.isfile(caret):
                shutil.move(caret, os.path.join(good_images_dir, os.path.basename(caret)))
        if os.path.isfile(caret):
            shutil.move(caret, os.path.join(bad_images_dir, os.path.basename(caret)))

