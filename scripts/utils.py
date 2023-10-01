import os
import onnxruntime as rt
import numpy as np
import cv2
import PIL.Image as pilimg
import shutil
from huggingface_hub import hf_hub_download
from transformers import pipeline
import requests

def read_lines(db) -> list[str]:
    with open(db, 'r+') as f:
        return f.read().splitlines() 

def save_line(db, already_downloaded):
    f = open(db, "a")
    f.write( already_downloaded + "\n")
    f.close()

def prepend_text(filename, line):
    with open(filename, 'r+') as f:
        content = line + f.read()
        f.seek(0, 0)
        f.write(content)

cafeai = None
anime_aesthetic = None

def classifier1(path, cafeai_treshold, trash_folder = None):
    global cafeai
    if cafeai is None:
        cafeai = pipeline("image-classification", model="cafeai/cafe_aesthetic", device = 0)

    if os.path.isfile(path) != True:
        return 0

    output = cafeai(path)
    item = output[0]
    if item["label"] != "aesthetic":
        item = output[1]
    score = item["score"]
    if score < cafeai_treshold:
        if trash_folder != None:
            target_path = trash_folder + path[path.rindex('/'):]
            shutil.move(path,target_path)
        else:
            os.remove(path)
        print("Removing file " + path + " - cafe_ai score too low - " + str(score) )
    else:
        print("Passed " + path + " - cafe_ai  - " + str(score) )
    
    return score

def classifier2(path, anime_aesthetic_treshold, trash_folder = None):
    global anime_aesthetic
    if anime_aesthetic is None:
        anime_aesthetic_path = hf_hub_download(repo_id="skytnt/anime-aesthetic", filename="model.onnx")
        anime_aesthetic = rt.InferenceSession(anime_aesthetic_path, providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])

    if os.path.isfile(path) != True:
        return 0

    img = np.array(pilimg.open(path).convert('RGB'))
    img = img.astype(np.float32) / 255
    s = 768
    h, w = img.shape[:-1]
    h, w = (s, int(s * w / h)) if h > w else (int(s * h / w), s)
    ph, pw = s - h, s - w
    img_input = np.zeros([s, s, 3], dtype=np.float32)
    img_input[ph // 2:ph // 2 + h, pw // 2:pw // 2 + w] = cv2.resize(img, (w, h))
    img_input = np.transpose(img_input, (2, 0, 1))
    img_input = img_input[np.newaxis, :]
    pred = anime_aesthetic.run(None, {"img": img_input})[0].item()

    if pred < anime_aesthetic_treshold:
        if trash_folder != None:
            target_path = os.path.join(trash_folder, os.path.basename(path))
            shutil.move(path,target_path)
        else:
            os.remove(path)
        print("Removing file " + path + " - anime_aesthetic score too low - " + str(pred) )
    else:
        print("Passed " + path + " - anime_aesthetic  - " + str(pred) )
    
    return pred

def download_image(url, target_folder):
    try:
        is_image = ".png" in url or ".jpeg" in url or ".jpg" in url
        if is_image != True:
            print(url + " is not an image")
            return None
        data = requests.get(url).content
        path = target_folder + url[url.rindex('/'):]
        open(path,'wb+').write(data)
        print("downloading " + url)
        return path
    except Exception as e:
        print("Failed to download " + url)
        print(e)
        return None