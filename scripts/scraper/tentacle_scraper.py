from .base_scraper import Scraper
import requests
from bs4 import BeautifulSoup

_base_path = 'https://tentaclerape.net'
def _get_images(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    a = soup.find_all('a', class_='thumb shm-thumb shm-thumb-link')
    hrefs = []
    for href in a:
        id = href["data-post-id"]
        hrefs.append(_base_path + "/index.php?q=/image/" + id + ".png")
        
    return list(set(hrefs))

# Supports only one tag search
class TentacleScraper(Scraper):
    def __init__(self, already_downloaded_urls_path: str, prompts_path: str, delay_between_downloads: float = 0):
        Scraper.__init__(self, already_downloaded_urls_path=already_downloaded_urls_path, prompts_path=prompts_path, delay_between_downloads=delay_between_downloads)
    
    def parse(self, count, tags):
        items=-1
        page = 0
        while items < count:
            page+=1
            page_url = _base_path + "/post/list/" + tags[0] + "/" + str(page)
            image_urls = _get_images(page_url)
            items = len(image_urls)

            for image in image_urls:
                file_path = self.download_file(image)
                caret_path = file_path[0:file_path.rindex('.')] + ".txt"
                caret_file = open(caret_path, 'w+')
                content = ",".join(tags)
                caret_file.write(content)
                caret_file.close()