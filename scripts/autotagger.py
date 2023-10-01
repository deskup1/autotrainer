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
from PIL import Image
import time
import shutil

blacklist = ["loli", "comic", "disembodied_penis" ]

folders = ["classified"]
target_folder = "tagged"
trash_folder = None
max_in_folder = 2000
default_tag_weight = 0.44
min_tag_treshold = 0.43

use_model1 = True
use_model2 = False

def load_model(model_repo: str, model_filename: str) -> rt.InferenceSession:
    path = huggingface_hub.hf_hub_download(model_repo, model_filename)
    model = rt.InferenceSession(path, providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
    return model

def load_labels(model_repo: str, label_filename: str) -> list[str]:
    path = huggingface_hub.hf_hub_download(model_repo, label_filename )
    df = pd.read_csv(path)

    tag_names = df["name"].tolist()
    rating_indexes = list(np.where(df["category"] == 9)[0])
    general_indexes = list(np.where(df["category"] == 0)[0])
    character_indexes = list(np.where(df["category"] == 4)[0])
    return tag_names, rating_indexes, general_indexes, character_indexes


labels1 = {}
classifier1 = {}
if use_model1:
    labels1 = load_labels("SmilingWolf/wd-v1-4-vit-tagger-v2", "selected_tags.csv")
    classifier1 = load_model("SmilingWolf/wd-v1-4-vit-tagger-v2", "model.onnx")

labels2 = {}
classifier2 = {}
if use_model2 == True:
    labels2 = load_labels("SmilingWolf/wd-v1-4-convnextv2-tagger-v2", "selected_tags.csv")
    classifier2 = load_model("SmilingWolf/wd-v1-4-convnextv2-tagger-v2", "model.onnx")



def smart_imread(img, flag=cv2.IMREAD_UNCHANGED):
    if img.endswith(".gif"):
        img = Image.open(img)
        img = img.convert("RGB")
        img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    else:
        img = cv2.imread(img, flag)
    return img


def smart_24bit(img):
    if img.dtype is np.dtype(np.uint16):
        img = (img / 257).astype(np.uint8)

    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    elif img.shape[2] == 4:
        trans_mask = img[:, :, 3] == 0
        img[trans_mask] = [255, 255, 255, 255]
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    return img


def make_square(img, target_size):
    old_size = img.shape[:2]
    desired_size = max(old_size)
    desired_size = max(desired_size, target_size)

    delta_w = desired_size - old_size[1]
    delta_h = desired_size - old_size[0]
    top, bottom = delta_h // 2, delta_h - (delta_h // 2)
    left, right = delta_w // 2, delta_w - (delta_w // 2)

    color = [255, 255, 255]
    new_im = cv2.copyMakeBorder(
        img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color
    )
    return new_im


def smart_resize(img, size):
    # Assumes the image has already gone through make_square
    if img.shape[0] > size:
        img = cv2.resize(img, (size, size), interpolation=cv2.INTER_AREA)
    elif img.shape[0] < size:
        img = cv2.resize(img, (size, size), interpolation=cv2.INTER_CUBIC)
    return img



def predict(
    image: PIL.Image.Image,
    model: rt.InferenceSession,
    general_threshold: float,
    character_threshold: float,
    tag_names: list[str],
    rating_indexes: list[np.int64],
    general_indexes: list[np.int64],
    character_indexes: list[np.int64],
):
    
    _, height, width, _ = model.get_inputs()[0].shape

    # Alpha to white
    image = image.convert("RGBA")
    new_image = PIL.Image.new("RGBA", image.size, "WHITE")
    new_image.paste(image, mask=image)
    image = new_image.convert("RGB")
    image = np.asarray(image)

    # PIL RGB to OpenCV BGR
    image = image[:, :, ::-1]

    image = make_square(image, height)
    image = smart_resize(image, height)
    image = image.astype(np.float32)
    image = np.expand_dims(image, 0)

    input_name = model.get_inputs()[0].name
    label_name = model.get_outputs()[0].name
    probs = model.run([label_name], {input_name: image})[0]

    labels = list(zip(tag_names, probs[0].astype(float)))

    # First 4 labels are actually ratings: pick one with argmax
    ratings_names = [labels[i] for i in rating_indexes]
    rating = dict(ratings_names)

    # Then we have general tags: pick any where prediction confidence > threshold
    general_names = [labels[i] for i in general_indexes]
    general_res = [x for x in general_names if x[1] > general_threshold]
    general_res = dict(general_res)

    # Everything else is characters: pick any where prediction confidence > threshold
    character_names = [labels[i] for i in character_indexes]
    character_res = [x for x in character_names if x[1] > character_threshold]
    character_res = dict(character_res)

    b = dict(sorted(general_res.items(), key=lambda item: item[1], reverse=True))
    a = (
        ", ".join(list(b.keys()))
        .replace("_", " ")
        .replace("(", "\(")
        .replace(")", "\)")
    )
    c = ", ".join(list(b.keys()))

    return (a, c, rating, character_res, general_res)


def tag_image(image_path, caret_path, target_path, caret_target_path):
    image = Image.open(image_path).convert('RGB')

    tags = {}
    if os.path.isfile(caret_path):
        columns = pd.read_csv(caret_path).columns.tolist()
        columns = [sub.strip().replace(' ', '_').replace("(","").replace(")","") for sub in columns]
        for tag in columns:
            tags[tag] = default_tag_weight

    if use_model1:
        results1 = predict(image, classifier1, 0.1, 0.1, labels1[0], labels1[1], labels1[2], labels1[3])
        for tag in results1[4].keys():
            updated_tag=tag.replace(' ', '_').replace("(","").replace(")","")
            if updated_tag in tags:
                tags[updated_tag] = tags[updated_tag] + results1[4][tag]
            else:
                tags[updated_tag] = results1[4][tag]
    
    if use_model2:
        results2 = predict(image, classifier2, 0.1, 0.1, labels2[0], labels2[1], labels2[2], labels2[3])
        for tag in results2[4].keys():
            updated_tag=tag.replace(' ', '_').replace("(","").replace(")","")
            if updated_tag in tags:
                tags[updated_tag] = tags[updated_tag] + results2[4][tag]
            else:
                tags[updated_tag] = results2[4][tag]

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

    shutil.move(image_path, target_path)
    if os.path.isfile(caret_path):
        os.remove(caret_path)

    print("Tagged " + image_path)

def tag():
    for folder in folders:
        if os.path.isdir(folder) == False:
            continue
        for item in os.listdir(folder):
            if (len(os.listdir(target_folder))) > max_in_folder:
                print("Exceed maximum number of files in folder, sleeping")
                while len(os.listdir(target_folder)) > max_in_folder:
                    time.sleep(10)

            image_path = folder + "/" + item
            caret_path = folder + "/" + item[0:item.rindex('.')] + ".txt"
            target_path = target_folder + "/" + item
            caret_target_path = target_folder + "/" + item[0:item.rindex('.')] + ".txt"
            try:
                is_image = item.endswith(".png") or item.endswith(".jpg") or item.endswith(".jpeg")
                if is_image == False:
                    continue

                tag_image(image_path, caret_path, target_path, caret_target_path)
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
                    print("Failed to remove " + image_path)
                try:
                    if trash_folder != None:
                        shutil.move(caret_path, os.path.join(trash_folder, item[0:item.rindex('.')] + ".txt"))
                    else:
                        os.remove(caret_path)
                except Exception as e:
                    print("Failed to remove " + caret_path)
                try:
                    if trash_folder != None:
                        shutil.move(target_path, os.path.join(trash_folder, item))
                    else:
                        os.remove(target_path)
                except Exception as e:
                    print("Failed to remove " + target_path)
                try:
                    if trash_folder != None:
                        shutil.move(caret_target_path, os.path.join(trash_folder, item[0:item.rindex('.')] + ".txt"))
                    else:
                        os.remove(caret_target_path)
                except Exception as e:
                    print("Failed to remove " + caret_target_path)


if __name__ == "__main__":
    while True:
        try:
            tag()
        except Exception as e:
            print(e)