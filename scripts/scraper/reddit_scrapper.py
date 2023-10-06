from .base_scraper import Scraper, save_tags_for_file, get_tags_for_file

import praw
import queue
import os

# Hack for getting more than 1000 posts via reddit api
class RedditIterator:
    def __init__(self, subreddit, supported_ext = [".jpeg", ".jpg", ".png" , ".bmp"]):
        self.posts = set()
        self.supported_ext = supported_ext
        self.queue = queue.Queue()
        self.queue.put(subreddit.new(limit=None))
        self.queue.put(subreddit.hot(limit=None))

        times = ["hour", "day",  "month", "week",  "year" , "all"]
        for time in times:
            self.queue.put(subreddit.top(limit=None, time_filter=time))

        for time in times:
            self.queue.put(subreddit.controversial(limit=None, time_filter=time))
        
        self.subreddit = None

    def __iter__(self):
        return self

    def __next__(self) -> str:

        url = None
        while url is None:
            if self.subreddit == None:
                if self.queue.empty():
                    raise StopIteration
                self.subreddit = self.queue.get()

            post = next(self.subreddit, None)

            if post is None:
                self.subreddit = None
                continue

            if post.id in self.posts:
                continue

            self.posts.add(post.id)

            for ext in self.supported_ext:
                if post.url.endswith(ext):
                    url = post.url
                    break
        return url

class RedditScraper(Scraper):
    def __init__(self, 
                 already_downloaded_urls_path: str, 
                 prompts_path: str,
                 app_id: str,
                 app_key: str,
                 delay_between_downloads: float = 0,
                 prepend_prompt_tags = False,
                 file_postprocessors = [],
                 use_urllib = False,
                 max_download_tries = 100
                ):
        
        self.prepend_prompt_tags = prepend_prompt_tags
        self.max_download_tries = max_download_tries

        self.reddit=praw.Reddit(
            client_id=app_id,
            client_secret=app_key,
            user_agent="scraper",
        )

        Scraper.__init__(self, 
                         already_downloaded_urls_path=already_downloaded_urls_path, 
                         prompts_path=prompts_path, 
                         delay_between_downloads=delay_between_downloads,
                         file_postprocessors=file_postprocessors,
                         use_urllib=use_urllib
                         )
        
    def parse(self, count, tags):

        if len(tags) == 0:
            return

        subreddit = self.reddit.subreddit(tags[0])
        iterator = RedditIterator(subreddit)

        images_download_tries = 0
        downloaded_images = 0
        for url in iterator:

            try:

                if self.is_url_already_downloaded(url):
                    continue
                if images_download_tries >= self.max_download_tries:
                    return
                if downloaded_images >= count:
                    return
            
                images_download_tries += 1

                downloaded_file = self.download_file(url)

                if downloaded_file is not None and os.path.isfile(downloaded_file) == False:
                    images_download_tries=0
                
                caret_file = downloaded_file[0:downloaded_file.rindex('.')] + ".txt"
                self.move_to_target_path(downloaded_file, caret_file)

                downloaded_images += 1

                print("r/" + tags[0] + " " + str(downloaded_images) + "/" + str(count))
            except Exception as e:
                print("Failed to download " + str(url))
                print(e)
