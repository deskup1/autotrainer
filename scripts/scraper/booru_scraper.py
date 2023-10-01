from .base_scraper import Scraper
import booru
import asyncio

class BooruScraper(Scraper):
    def __init__(self, booru, already_downloaded_urls_path: str, prompts_path: str, delay_between_downloads: float = 0):
        self.booru = booru
        Scraper.__init__(self, already_downloaded_urls_path=already_downloaded_urls_path, prompts_path=prompts_path, delay_between_downloads=delay_between_downloads)
    
    def parse(self, count, tags):
        results = []

        loop = asyncio.get_event_loop()

        page = 0
        current_count = 0

        while current_count <=  count:
            try:
                results = []
                files= []
                for n in range(3):
                    task = self.booru.search(query=" ".join(tags), page=page, limit=100)
                    results = loop.run_until_complete(task)
                    results = booru.resolve(results)
                    if len(results) != 0:
                        break

                print("No results on page " + str(page) + " on " + str(n+1) + " try")
                print("Got " + str(len(results)) + " posts")

                for result in results:
                    if self.is_url_already_downloaded(result['file_url']):
                        continue
                    files.append(result)
                
                page+=1
                
                for file in files:
                    current_count += 1
                    try:
                        downloaded_file = self.download_file(file['file_url'])
                        if downloaded_file == None:
                            continue

                        downloaded_tags = self.save_tags_for_file(file['tags'], downloaded_file)

                        self.move_to_target_path(downloaded_file, downloaded_tags)

                    except Exception as e:
                        print(e)

            except Exception as e:
                print(e)

            if len(results) == 0:
                break