import os
import pandas as pd
import time
import shutil
from tagger.wd14_tagger import Wd14Tagger

from genericpath import isdir
from transformers import pipeline
import os
import PIL.Image
import piexif
import numpy as np
import huggingface_hub
import onnxruntime as rt
import cv2
import pandas as pd
import numpy as np
import time
import shutil

blacklist = ["loli", "comic", "disembodied_penis" ]
supported_extensions = [".jpeg", ".jpg", ".png"]

source_folders = ["images/aesthetic"]
target_folder = "images/tagged"
trash_folder = None
max_in_folder = 2000

default_tag_weight = 0.44
min_tag_treshold = 0.43

classifiers = [
    Wd14Tagger("SmilingWolf/wd-v1-4-vit-tagger-v2"),
    Wd14Tagger("SmilingWolf/wd-v1-4-convnextv2-tagger-v2"),
    ]

# get tags merged from multiple tagging models and caret file
def tag_image(image_path, target_path,  caret_path = None, caret_target_path = None):

    tags = {}
    if caret_target_path != None and caret_path != None and os.path.isfile(caret_path):
        columns = pd.read_csv(caret_path).columns.tolist()
        columns = [sub.strip().replace(' ', '_').replace("(","").replace(")","") for sub in columns]
        for tag in columns:
            tags[tag] = default_tag_weight
    
    for classifier in classifiers:
        print("Tagging " + image_path + " using " + classifier.name)
        results = classifier.tags(image_path)
        for tag in results[4].keys():
            updated_tag=tag.replace(' ', '_').replace("(","").replace(")","")
            if updated_tag in tags:
                tags[updated_tag] = tags[updated_tag] + results[4][tag]
            else:
                tags[updated_tag] = results[4][tag]
    
    tags = sorted(tags.items(), key=lambda x:x[1], reverse=True)
    print(tags)

    sorted_tags = []
    for tag in tags:
        if tag[1] > min_tag_treshold:
            sorted_tags.append(tag[0])
    
    for tag in blacklist:
        for sorted_tag in sorted_tags:
            if tag.replace(" ", "_") == sorted_tag:
             raise Exception("Found blacklisted tag " + tag + " in " + image_path)

    caret_file = open(caret_target_path, 'w')
    content = ", ".join(sorted_tags).replace("_", " ").replace("(","").replace(")","")
    caret_file.write(content)
    caret_file.close()

    print("Moving " + image_path + " to " + target_path)
    shutil.move(image_path, target_path)
    if os.path.isfile(caret_path):
        os.remove(caret_path)

    print("Tagged " + image_path)

# tags images in source_folders and moves them to target_folder
def tag():
    for folder in source_folders:

        if os.path.isdir(folder) == False:
            continue

        items = os.listdir(folder)
        for item in items:
            if (len(os.listdir(target_folder))) > max_in_folder:
                print("Exceed maximum number of files in folder, sleeping")
                while len(os.listdir(target_folder)) > max_in_folder:
                    time.sleep(10)
            
            filename = os.path.basename(item)
            _, file_extension = os.path.splitext(filename)
            is_supported = file_extension in supported_extensions
            if is_supported == False:
                continue

            image_path = os.path.join(folder, filename)
            caret_path = os.path.join(folder, filename[0:filename.rindex('.')] + ".txt")

            target_path = os.path.join(target_folder, os.path.basename(filename))
            caret_target_path = os.path.join(target_folder, filename[0:filename.rindex('.')] + ".txt")

            try:
                tag_image(image_path, target_path, caret_path, caret_target_path)
            except Exception as e:
                print("Failed to tag file " + item)
                print(e)
                try:
                    if os.path.isfile(image_path):
                        if trash_folder != None:
                            shutil.move(image_path, os.path.join(trash_folder, item))
                        else:
                            os.remove(image_path)
                except Exception as e:
                    print("Failed to remove " + caret_path)
                try:
                    if os.path.isfile(caret_path):
                        if trash_folder != None:
                            shutil.move(caret_path, os.path.join(trash_folder, item))
                        else:
                            os.remove(caret_path)
                except Exception as e:
                    print("Failed to remove " + caret_path)


if __name__ == "__main__":
    print("Started tagger")
    while True:
        try:
            tag()
            time.sleep(2)
        except Exception as e:
            print(e)