import os
import random
import time
import shutil
import requests
from urllib.request import urlopen
from shutil import copyfileobj


def get_tags_for_file(filename: str) -> list[str] | None:
    caret_path = filename[0:filename.rindex('.')] + ".txt"
    try:
        caret_file = open(caret_path, 'r')
        tags = caret_file.read().replace("_", " ").replace("(","").replace(")","").split(",")
        return [s.strip() for s in tags]
    except OSError:
        return None


def save_tags_for_file(tags: list[str], filename: str) -> str | None:
    caret_path = filename[0:filename.rindex('.')] + ".txt"
    caret_file = open(caret_path, 'w')
    content = ", ".join(tags).replace("_", " ").replace("(","").replace(")","")
    caret_file.write(content)
    caret_file.close()
    return caret_path

class Scraper:
    def __init__(self, 
                 already_downloaded_urls_path: str,
                 download_path: str = "images/download-cache",
                 max_files_in_download_path = 100,
                 target_path: str = "images/download", 
                 max_files_in_target_path = None,
                 prompts_path: str = "prompts.txt",
                 supported_extensions = [".jpeg", ".jpg", ".png"],
                 delay_between_downloads = 0.0,
                 file_postprocessors = [],
                 use_urllib = False,
                 ):
        self.use_urllib = use_urllib
        self.delay_between_downloads = delay_between_downloads

        self.already_downloaded_urls_path = already_downloaded_urls_path

        self.download_path = download_path
        self.max_files_in_download_path = max_files_in_download_path

        self.target_path = target_path
        self.max_files_in_target_path = max_files_in_target_path

        self.prompts_path = prompts_path

        self.supported_extensions = supported_extensions

        self.file_postprocessors = file_postprocessors

        self.already_downloaded_urls: list[str] = []
        try:
            with open(self.already_downloaded_urls_path, 'r+') as f:
                self.already_downloaded_urls = f.read().splitlines() 
        except:
            print("Failed to open file " + self.already_downloaded_urls_path + ", creating new one")
            open(self.already_downloaded_urls_path, "x").close()


    def _save_already_downloaded_url(self, url: str):
        url = url.strip()
        if url == "":
            return
        
        self.already_downloaded_urls.append(url)

        f = open(self.already_downloaded_urls_path, "a")
        f.write(url + "\n")
        f.close()

    def is_url_already_downloaded(self, url: str) -> bool:
        if url is None or url.strip() == "":
            return True
        return url in self.already_downloaded_urls
    
    def move_to_target_path(self, file_path, caret_path = None) -> str | None:
            
        if file_path is None or os.path.isfile(file_path) == False:
            return None

        if  self.max_files_in_target_path != None and len(os.listdir(self.target_path)) > self.max_files_in_target_path:
            print("Exceed maximum number of files in target folder, sleeping")
            while len(os.listdir(self.target_path)) > self.max_files_in_target_path:
                time.sleep(10)

        if os.path.isfile(file_path):
            target_path = os.path.join(self.target_path, os.path.basename(file_path))
            shutil.move(file_path, target_path)

        if caret_path is not None and os.path.isfile(caret_path):
            target_path = os.path.join(self.target_path, os.path.basename(caret_path))
            shutil.move(caret_path, target_path)    


    def download_file(self, url, target_file = None) -> str | None:

        if url is None:
            return None

        time.sleep(self.delay_between_downloads)

        if self.max_files_in_download_path != None and len(os.listdir(self.download_path)) > self.max_files_in_download_path:
            print("Exceed maximum number of files in download folder, sleeping")
            while len(os.listdir(self.download_path)) > self.max_files_in_download_path:
                time.sleep(10)

        self._save_already_downloaded_url(url)
        try:
            filename = target_file
            if filename is None:
                filename = url[url.rindex('/')+1:]

            _, file_extension = os.path.splitext(filename)
            is_supported= file_extension in self.supported_extensions
            if is_supported != True:
                print(url + " is not supported")
                return None
            
            print("Downloading " + url)

            download_path = os.path.join(self.download_path, filename)
            if self.use_urllib:
                with urlopen(url) as in_stream, open(download_path, 'wb+') as out_file:
                    copyfileobj(in_stream, out_file)
            else:
                res = requests.get(url, stream = True)
                if res.status_code == 200:
                    with open(download_path,'wb') as f:
                        shutil.copyfileobj(res.raw, f)
                else:
                    raise Exception("Failed to download file, status: " + str(res.status_code))

            if os.path.exists(download_path):
                for postprocessor in self.file_postprocessors:
                    postprocessor(download_path)
                return download_path
            else:
                return None

        except Exception as e:
            print("Failed to download " + url)
            print(e)
        return None
    
    
    def parse(self, count, tags):
        return
    
    def _get_prompts(self) -> list:
        prompts = []
        result = []
        with open(self.prompts_path, 'r+') as f:
            prompts = f.read().splitlines() 
        for prompt in prompts:
            try:
                lines = prompt.split(", ")
                count = int(lines[0])
                tags = lines[1:]
                result.append((count, tags))

            except Exception as e:
                print("Failed to parse " + prompt)
                print(e)

        print("Prompts [" + str(len(result)) + "] in file " + self.prompts_path)
        for r in result:
            print(str(r[0]) + " - " + str(r[1]))
        return result
    
    def scrape(self):
        prompts = self._get_prompts()
        for prompt in prompts:
            print("Started scraping: " + str(prompt[0]) + " - " + str(prompt[1]))
            self.parse(prompt[0], prompt[1])
    
    def start(self,):
        print("Started scraper")
        while True:
            self.scrape()