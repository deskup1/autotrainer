from genericpath import isfile
import os
import shutil
import difPy
import time
import subprocess

train_script = "train.sh"
copy_folders = ['base']
move_folders = ['tagged']
dataset_path = "dataset"
keep_nth_model = 3

model_name = 'saxime.safetensors'

train_count = 0

def get_associated_images(path) -> list[str]:
    associated_images = []
    for item in os.listdir(path):
        if item.endswith(".txt"):
            continue
        
        caret_path = os.path.join(path, item[0:item.rindex('.')] + ".txt")
        item_path = os.path.join(path, item)
        if os.path.isfile(caret_path) and os.path.isfile(item_path):
            associated_images.append([caret_path, item_path])

    return associated_images

def copy_assosiated(copy):
        target_path1 = os.path.join(dataset_path, os.path.basename(copy[0]))
        target_path2 = os.path.join(dataset_path, os.path.basename(copy[1]))
        try:
            shutil.copy(copy[0], target_path1)
            shutil.copy(copy[1], target_path2)
        except Exception as e:
            if os.path.isfile(target_path1):
                try:
                    os.remove(target_path1)
                except Exception as e:
                    print("Failed to remove " + target_path1)
            if os.path.isfile(target_path2):
                try:
                    os.remove(target_path2)
                except Exception as e:
                    print("Failed to remove " + target_path2)

def move_assosiated(copy):
        target_path1 = os.path.join(dataset_path, os.path.basename(copy[0]))
        target_path2 = os.path.join(dataset_path, os.path.basename(copy[1]))
        try:
            shutil.move(copy[0], target_path1)
            shutil.move(copy[1], target_path2)
        except Exception as e:
            if os.path.isfile(target_path1):
                try:
                    os.remove(target_path1)
                except Exception as e:
                    print("Failed to remove " + target_path1)
            if os.path.isfile(target_path2):
                try:
                    os.remove(target_path2)
                except Exception as e:
                    print("Failed to remove " + target_path2)


def remove_duplicates():
    print("Remove duplicates")
    dif = difPy.build([os.curdir + "/" + dataset_path])
    search = difPy.search(dif, similarity=0.91)
    for image in search.lower_quality["lower_quality"]:
        os.remove(image)
        caret_path = image[0:image.rindex('.')] + ".txt"
        if os.path.isfile(caret_path):
            os.remove(caret_path)

def prepare_dataset():
    print("Prepare dataset")

    if os.path.exists(dataset_path) and os.path.isdir(dataset_path):
        shutil.rmtree(dataset_path)
    os.makedirs(dataset_path)

    copy_items = []
    for copy in copy_folders:
        if os.path.isdir(copy):
            copy_items += get_associated_images(copy)
    
    move_items = []
    for move in move_folders:
        if os.path.isdir(move):
            move_items += get_associated_images(move)
    
    for copy in copy_items:
        move_assosiated(copy)
    
    for move in move_items:
        move_assosiated(move)
    
def call_training_script():
    global train_count
    train_count += 1
    print("Start training")

    print(subprocess.run([train_script], shell=True, executable="/bin/bash"))

    if os.path.isfile(model_name) == False:
        print(model_name + " not found after train, exciting")
        exit()

    if os.path.isfile("base-" + model_name):
        if train_count % keep_nth_model == 0:
            os.rename("base-" + model_name, str(train_count) + "-" + model_name)
        else:
            os.remove("base-" + model_name)
        os.rename(model_name, "base-" + model_name)


def train():

    prepare_dataset()
    while len(os.listdir(dataset_path)) == 0:
        print("Directory " + dataset_path + " is empty, cannot continue")
        time.sleep(30)
        prepare_dataset()
    
    
    remove_duplicates()
    call_training_script()
    

if __name__ == '__main__':
    while True:
        train()

