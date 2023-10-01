from .base_aesthetic_classifier import AestheticClassifier

from transformers import pipeline
import os


class HfPipelineAestheticClassifier(AestheticClassifier):
    def __init__(self, model_name: str, device = 0, label_name = "aesthetic"):
        super().__init__()
        self.model_name = model_name
        self.label_name = label_name
        self.pipeline = pipeline("image-classification", model=model_name, device = device)
    
    def score(self, image_path: str):

        if os.path.isfile(image_path) != True:
            return 0

        score = 0
        outputs = self.pipeline(image_path)
        for output in outputs:
            if output["label"] == self.label_name:
                score = output["score"]

                print(self.model_name + " - " + image_path + ":" + str(score))
                return score
    
        print("Label " + self.label_name + " not found")
        return score
