import os
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
import numpy as np
import time
import shutil
from scraper.base_scraper import get_tags_for_file, save_tags_for_file

blacklist = ["loli", "comic", "disembodied_penis" ]
supported_extensions = [".jpeg", ".jpg", ".png"]

source_folders = ["images/aesthetic"]
target_folder = "images/tagged"
trash_folder = None
max_in_folder = 2000

default_tag_weight = 0.44
min_tag_treshold = 0.43

include_character_tags = True
include_rating_tags = True

classifiers = [
    Wd14Tagger("SmilingWolf/wd-v1-4-vit-tagger-v2"),
    Wd14Tagger("SmilingWolf/wd-v1-4-convnextv2-tagger-v2"),
    ]

# get tags merged from multiple tagging models and caret file
def tag_image(image_path, caret_path = None):

    if image_path is None or os.path.isfile(image_path) == False:
        return
    
    if caret_path is None:
        new_path = image_path[0:image_path.rindex('.')] + ".txt"
        if os.path.isfile(new_path):
            caret_path=new_path

    _target_folder = target_folder
    if _target_folder is None:
        _target_folder = os.path.dirname(image_path)

    tags = {}
    if caret_path is not None and os.path.isfile(caret_path) == True:
        columns = get_tags_for_file(caret_path)
        if columns is None:
            columns = []
        columns = [sub.strip().replace(' ', '_').replace("(","").replace(")","") for sub in columns]
        for tag in columns:
            tags[tag] = default_tag_weight
    
    for classifier in classifiers:
        print("Tagging " + image_path + " using " + classifier.name)
        results = classifier.tags(image_path)

        # set rating tag
        if include_rating_tags:
            rating_tags = list(results[2].items())
            rating = rating_tags[0]
            for rating_tag in rating_tags:
                if rating_tag[1] > rating[1]:
                    rating = rating_tag

            if rating[0] == "general" or rating[0] == "sensitive":
                tags["sfw"] = rating[1] + tags.get("sfw", 0)
            elif rating[0] == "explicit" or rating[0] == "questionable":
                tags["nsfw"] = rating[1] + tags.get("nsfw", 0)


        # set character tag
        if include_character_tags:
            character_tags = list(results[3].items())
            for tag in character_tags:
                updated_tag=tag[0].replace(' ', '_').replace("(","").replace(")","")
                tags[updated_tag] =  tag[1] + tags.get(updated_tag, 0)

        # set general tags
        for tag in results[4].keys():
            updated_tag=tag.replace(' ', '_').replace("(","").replace(")","")
            tags[updated_tag] =  results[4][tag] + tags.get(updated_tag, 0)
    
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

    if caret_path is None:
        caret_path = image_path[0:image_path.rindex('.')] + ".txt"
    
    print("Saving tags to " + caret_path)
    caret_file = save_tags_for_file(sorted_tags, caret_path)

    if target_folder is not None:
        target_path = os.path.join(_target_folder, os.path.basename(image_path))
        caret_target_path = os.path.join(_target_folder, os.path.basename(caret_path))
        print("Moving " + image_path + " to " + target_path)
        shutil.move(image_path, target_path)
        shutil.move(caret_file, caret_target_path)

    print("Tagged " + image_path)

# tags images in source_folders and moves them to target_folder
def tag():
    for folder in source_folders:

        if os.path.isdir(folder) == False:
            continue

        items = os.listdir(folder)
        for item in items:
            if target_folder is not None and (len(os.listdir(target_folder))) > max_in_folder:
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

            try:
                tag_image(image_path, caret_path)
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