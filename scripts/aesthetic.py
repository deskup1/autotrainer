import os
import shutil
import time

from aesthetic.anime_aesthetic_classifier import AnimeAestheticClassifier
from aesthetic.hf_pipeline_aesthetic_classifier import HfPipelineAestheticClassifier
from aesthetic.base_aesthetic_classifier import AestheticClassifier

anime_aesthetic_pass_treshold = 0.78
anime_aesthetic_quality_tresholds = [
    (1, 0.93, "best quality"), 
    (0.93, 0.89, "good quality"),
    (0.60, 0.50, "bad quality"),
    (0.50, 0.00, "worst quality"),
    ]

cafeai_pass_treshold = 0.9
cafeai_aesthetic_quality_tresholds = []

source_folders = ["images/download"]
trash_folder = None
target_folder = "images/aesthetic"
supported_extensions = [".jpeg", ".jpg", ".png"]

max_files_in_target_path = 100


classifiers = [
    (AnimeAestheticClassifier(), anime_aesthetic_pass_treshold, anime_aesthetic_quality_tresholds),
    (HfPipelineAestheticClassifier("cafeai/cafe_aesthetic"), cafeai_pass_treshold, cafeai_aesthetic_quality_tresholds)
]

def classify_image(path: str):
    if os.path.isfile(path) == False:
        return
    
    _, file_extension = os.path.splitext(path)
    is_supported= file_extension in supported_extensions

    if is_supported == False:
        return

    caret_path = path[0:path.rindex('.')] + ".txt"

    additional_tags = []
    for classifier in classifiers:
        pipeline: AestheticClassifier = classifier[0]
        pass_score = classifier[1]
        tresholds = classifier[2]

        score = pipeline.score(path)

        if score < pass_score:
            if trash_folder is not None:
                if os.path.isfile(path) == True:
                    shutil.move(path, os.path.join(trash_folder, os.path.basename(path)))
                if os.path.isfile(caret_path) == True:
                    shutil.move(caret_path, os.path.join(trash_folder, os.path.basename(caret_path)))
            else:
                if os.path.isfile(path) == True:
                    os.remove(path)
                if os.path.isfile(caret_path) == True:
                    os.remove(caret_path)
            return score
        
        for treshold in tresholds:
            if score <= treshold[0] and score > treshold[1]:
                additional_tags.append(treshold[2])

    if os.path.isfile(caret_path):
        with open(caret_path, 'r+') as f:
            content = ", ".join(additional_tags) + ", " + f.read()
            f.seek(0, 0)
            f.write(content)

    if os.path.isfile(caret_path) == True:
        shutil.move(caret_path, os.path.join(target_folder, os.path.basename(caret_path)))
    if os.path.isfile(path) == True:
        shutil.move(path, os.path.join(target_folder, os.path.basename(path)))

    message = "Image passed: " + path 
    if len(additional_tags) > 0:
        message + " with additional tags [" + ", ".join(additional_tags) + "]"
    print(message)

def classify():
    for folder in source_folders:
        if os.path.isdir(folder) == False:
            continue

        for item in os.listdir(folder):

            if (len(os.listdir(target_folder))) > max_files_in_target_path:
                print("Exceed maximum number of files in target folder, sleeping")
                while len(os.listdir(target_folder)) > max_files_in_target_path:
                    time.sleep(10)

            try:
                classify_image(os.path.join(folder, item))
            except Exception as e:
                print(e)

 
if __name__ == "__main__":
    print("Started aesthetic classifier")
    while True:
        classify()
