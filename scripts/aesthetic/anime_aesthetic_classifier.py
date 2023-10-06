from .base_aesthetic_classifier import AestheticClassifier

import os
import onnxruntime as rt
import numpy as np
import cv2
import PIL.Image as pilimg
from huggingface_hub import hf_hub_download

class AnimeAestheticClassifier(AestheticClassifier):
    def __init__(self):
        super().__init__()
        self.repo_id = "skytnt/anime-aesthetic"
        anime_aesthetic_path = hf_hub_download(repo_id=self.repo_id, filename="model.onnx")
        self.anime_aesthetic = rt.InferenceSession(anime_aesthetic_path, providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
    
    def score(self, image_path: str):

        if os.path.isfile(image_path) != True:
            return 0

        img = np.array(pilimg.open(image_path).convert('RGB'))
        img = img.astype(np.float32) / 255
        s = 768
        h, w = img.shape[:-1]
        h, w = (s, int(s * w / h)) if h > w else (int(s * h / w), s)
        ph, pw = s - h, s - w
        img_input = np.zeros([s, s, 3], dtype=np.float32)
        img_input[ph // 2:ph // 2 + h, pw // 2:pw // 2 + w] = cv2.resize(img, (w, h))
        img_input = np.transpose(img_input, (2, 0, 1))
        img_input = img_input[np.newaxis, :]
        pred = self.anime_aesthetic.run(None, {"img": img_input})[0].item()

        return pred