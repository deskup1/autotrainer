import os, fnmatch, random

def randomize(directory, filePattern):
    for path, dirs, files in os.walk(os.path.abspath(directory)):
        for filename in fnmatch.filter(files, filePattern):
            print("\n\n" + filename)
            filepath = os.path.join(path, filename)
            with open(filepath) as f:
                s = f.read()
            list = s.split(", ")
            random.shuffle(list)
            print(list)
            s = ", ".join(list)
            print(s)
            with open(filepath, "w") as f:
                f.write(s)

randomize("D:\dataset\image-classifier\images", "*.txt" )