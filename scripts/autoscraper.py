from scraper.booru_scraper import BooruScraper
from scraper.reddit_scrapper import RedditScraper
import booru
import sys
import os

import argparse
parser = argparse.ArgumentParser(
    prog="AutoScraper",
    description="Scrape images from multiple sities, filter out unaesthetic images, tag them."
)

parser.add_argument('scraper', help="name of the parser", type=str)
parser.add_argument("--prompts_file", help="path to file containing prompts", type=str, default="prompts.txt")
parser.add_argument("--db_file", help="path to db file", type=str, default=None)
parser.add_argument("--use_aesthetic", help="use scraper with aesthetic filter", action='store_true')
parser.add_argument("--aesthetic_anime_aesthetic_treshold", help="anime_aesthetic filter pass treshold (default:0.775)", type=float, default=0.775)
parser.add_argument("--aesthetic_cafeai_pass_treshold", help="anime_aesthetic filter pass treshold (default:0.9)", type=float, default=0.9)
parser.add_argument("--max_files_in_cache_folder", help="maximum files in cache folder, if exceeds then wait until space is available", type=int, default=100)
parser.add_argument("--max_files_in_download_folder", help="maximum files in download folder, if exceeds then wait until space is available", type=int, default=None)
parser.add_argument("--use_tagger", help="use scraper with tagger", action='store_true')
parser.add_argument("--looped", help="run scraper in a loop", action='store_true')
parser.add_argument("--prepend_prompt_tags", help="prepend tags from prompt file at the start of the caret file", action='store_true')
parser.add_argument("--skip_tags", help="don't add downloaded tags", action='store_true')
parser.add_argument("--use_urllib", help="use urllib library instead requests library for downloading images", action='store_true')
parser.add_argument("--reddit_app_id", help="reddit app id needed when using Reddit scraper", type=str, default=None)
parser.add_argument("--reddit_app_key", help="reddit app key needed when using Reddit scraper", type=str, default=None)

if __name__ == "__main__":

    args = parser.parse_args()

    booru_name = args.scraper
    if args.db_file is None:
        args.db_file = os.path.join("already-downloaded-urls", booru_name + ".txt")


    file_postproccesors = []
    if args.use_aesthetic:
        print("Setup autoaesthetic with tresholds " + str([args.aesthetic_anime_aesthetic_treshold, args.aesthetic_cafeai_pass_treshold]))
        import autoaesthetic
        autoaesthetic.target_folder = None
        autoaesthetic.anime_aesthetic_pass_treshold = float(args.aesthetic_anime_aesthetic_treshold)
        autoaesthetic.cafeai_pass_treshold = float(args.aesthetic_cafeai_pass_treshold)
        file_postproccesors.append(autoaesthetic.classify_image)
    
    if args.use_tagger:
        print("Setup autotagger")
        import autotagger
        autotagger.target_folder = None
        file_postproccesors.append(autotagger.tag_image)
    
    booru_obj = {}
    if booru_name == "Atfbooru":
        booru_obj = booru.Atfbooru()
    elif booru_name == "Behoimi":
        booru_obj = booru.Behoimi()
    elif booru_name == "Danbooru":
        booru_obj = booru.Danbooru()
        args.use_urllib = True
    elif booru_name == "Derpibooru":
        booru_obj = booru.Derpibooru(), 
    elif booru_name == "E621":
        booru_obj = booru.E621()
    elif booru_name == "E926":
        booru_obj = booru.E926()
    elif booru_name == "Furbooru":
        booru_obj = booru.Furbooru()
    elif booru_name == "Gelbooru":
        booru_obj = booru.Gelbooru()
    elif booru_name == "Hypnohub":
        booru_obj = booru.Hypnohub()
    elif booru_name == "Konachan":
        booru_obj = booru.Konachan()
    elif booru_name == "Konachan_Net":
        booru_obj = booru.Konachan_Net()
    elif booru_name == "Lolibooru":
        booru_obj = booru.Lolibooru()
    elif booru_name == "Paheal":
        booru_obj = booru.Paheal()
    elif booru_name == "Realbooru":
        booru_obj = booru.Realbooru()
    elif booru_name == "Rule34":
        booru_obj = booru.Rule34()
    elif booru_name == "Safebooru":
        booru_obj = booru.Safebooru()
    elif booru_name == "Xbooru":
        booru_obj = booru.Xbooru()
    elif booru_name == "Yandere":
        booru_obj = booru.Yandere()
    elif booru_name == "Reddit":
        scraper = RedditScraper(args.db_file, args.prompts_file, 
                                file_postprocessors=file_postproccesors,
                                prepend_prompt_tags=args.prepend_prompt_tags,
                                app_id=args.reddit_app_id,
                                app_key=args.reddit_app_key,
                                use_urllib=args.use_urllib,
                                max_files_in_download_path=args.max_files_in_cache_folder,
                                max_files_in_target_path=args.max_files_in_download_folder,
                                )
        if args.looped:
            scraper.start()
        else:
            scraper.scrape()
        exit()
    else:
        print(booru_name + " is not supported")
        exit()

    scraper = BooruScraper(booru_obj, args.db_file, args.prompts_file, 
                           file_postprocessors=file_postproccesors,
                           prepend_prompt_tags=args.prepend_prompt_tags,
                           skip_tags=args.skip_tags,
                           use_urllib=args.use_urllib,
                           max_files_in_download_path=args.max_files_in_cache_folder,
                           max_files_in_target_path=args.max_files_in_download_folder,
                           )
    if args.looped:
        scraper.start()
    else:
        scraper.scrape()