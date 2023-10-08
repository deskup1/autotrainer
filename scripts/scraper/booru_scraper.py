from .base_scraper import Scraper, save_tags_for_file, get_tags_for_file
import booru
import asyncio
import os
import random

class BooruScraper(Scraper):
    def __init__(self, 
                 booru, 
                 already_downloaded_urls_path: str, 
                 prompts_path: str, 
                 delay_between_downloads: float = 0,
                 skip_tags = False,
                 prepend_prompt_tags = False,
                 file_postprocessors = [],
                 use_urllib = False,
                 max_download_tries = 100,
                 max_files_in_download_path = 100,
                 max_files_in_target_path = 100
                ):
        self.booru = booru
        self.skip_tags = skip_tags
        self.prepend_prompt_tags = prepend_prompt_tags
        self.max_download_tries = max_download_tries
        Scraper.__init__(self, 
                         already_downloaded_urls_path=already_downloaded_urls_path, 
                         prompts_path=prompts_path, 
                         delay_between_downloads=delay_between_downloads,
                         file_postprocessors=file_postprocessors,
                         use_urllib=use_urllib,
                         max_files_in_download_path = max_files_in_download_path,
                         max_files_in_target_path = max_files_in_target_path
                         )
    
    def parse(self, count, tags: list[str]):

        tags = [s.replace(' ', '_') for s in tags]

        results = []

        loop = asyncio.get_event_loop()

        page = 0
        images_downloaded_count = 0
        images_download_tries = 0

        while images_downloaded_count <= count and images_download_tries <= self.max_download_tries:
            try:
                results = []
                files= []
                query = " ".join(tags)

                print("Query: " + query)
                for n in range(3):
                    task = self.booru.search(query=query, page=page, limit=100)
                    results = loop.run_until_complete(task)
                    results = booru.resolve(results)
                    if len(results) != 0:
                        break
                    print("No results on page " + str(page) + " on " + str(n+1) + " try")

                print("Got " + str(len(results)) + " posts")

                # append already downloaded url
                for result in results:
                    if self.is_url_already_downloaded(result.get('file_url', None)):
                        continue
                    files.append(result)
                
                print("Got " + str(len(results)) + " posts")
                
                page+=1
                
                
                for file in files:
                    if images_downloaded_count >= count or images_download_tries >= self.max_download_tries:
                        return

                    images_download_tries += 1

                    url = file.get('file_url', None)

                    filename = None
                    if self.prepend_prompt_tags:
                        filename = "_".join(filter(lambda x: x.startswith("-") == False, tags)) + "_" + url[url.rindex('/')+1:]
                    else:
                        filename = url[url.rindex('/')+1:]

                    try:
                        downloaded_file_path = self.download_file(url, filename)

                        # skip if failed to download
                        if downloaded_file_path is None or os.path.isfile(downloaded_file_path) == False:
                            continue

                        images_downloaded_count += 1

                        print(str(images_downloaded_count) + "/" + str(count) + " " + query)

                        # get tags
                        filetags = get_tags_for_file(downloaded_file_path)
                        if filetags is None:
                            filetags = []
                        # add tags from prompt
                        if self.prepend_prompt_tags:
                            tags.reverse()
                            for tag in tags:
                                if tag.startswith("-"):
                                    continue
                                while tag in filetags:
                                    filetags.remove(tag)
                                filetags.insert(0, tag)

                        # add tags
                        if self.skip_tags != True:
                            downloaded_tags = file.get('tags', [])
                            if len(filetags) == 0:
                                downloaded_tags = file.get('tag_string', [])
                            random.shuffle(downloaded_tags)
                            for downloaded_tag in downloaded_tags:
                                if downloaded_tag not in filetags:
                                    filetags.append(downloaded_tag)

                        downloaded_tags_path = save_tags_for_file(filetags, downloaded_file_path)

                        self.move_to_target_path(downloaded_file_path, downloaded_tags_path)

                        # reset download counter
                        images_download_tries = 0

                    except Exception as e:
                        print(e)

            except Exception as e:
                print(e)

            if len(results) == 0:
                break