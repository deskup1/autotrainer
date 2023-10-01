from transformers import pipeline
import glob
import shutil
import os.path
import difPy
import os


treshold = 0.96
batch_count = 32

imdir = 'images'
bad_images_dir = 'bad'
good_images_dir = 'good'

ext = ['png', 'jpg', 'bmp']

if __name__ == '__main__':

    images = []
    [images.extend(glob.glob( os.curdir + "/" + imdir + '/*.' + e)) for e in ext]
    print("images: " + str(len(images)))

    classifier = pipeline("image-classification", model="cafeai/cafe_aesthetic", device = 0)


    batch = []
    for id, image in enumerate(images):
        batch.append(image)
        if len(batch) == batch_count or id +1 >= (len(images)):
            outputs = classifier(images = batch)

            for output_id, output in enumerate(outputs):
                item = output[0]
                if item["label"] != "aesthetic":
                    item = output[1]
                score = item["score"]
                print(batch[output_id] + " : " + str(score))
                if score >= treshold:
                    shutil.move(batch[output_id], batch[output_id].replace(imdir, good_images_dir))
                    caret = batch[output_id].rsplit(".", 1)[0] + ".txt"
                    if os.path.isfile(caret):
                        shutil.move(caret, caret.replace(imdir, good_images_dir))
                else:
                    shutil.move(batch[output_id], batch[output_id].replace(imdir, bad_images_dir))
                    caret = batch[output_id].rsplit(".", 1)[0] + ".txt"
                    if os.path.isfile(caret):
                        shutil.move(caret, caret.replace(imdir, bad_images_dir))
            
            print(str(id+1) + "/" + str(len(images)))
            batch = []