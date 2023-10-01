from scraper.booru_scraper import BooruScraper
import booru
import sys
import os
db_path = "already-downloaded-urls"
prompts_file = "prompts.txt"

if __name__ == "__main__":

    if len(sys.argv) == 1:
        print("Booru not specified")
    
    booru_name = sys.argv[1]
    scraper = {}
    if booru_name == "Atfbooru":
        scraper = BooruScraper(booru.Atfbooru(), os.path.join(db_path, booru_name + ".txt"), prompts_file)
    elif booru_name == "Behoimi":
        scraper = BooruScraper(booru.Behoimi(), os.path.join(db_path, booru_name + ".txt"), prompts_file)
    elif booru_name == "Danbooru":
        scraper = BooruScraper(booru.Danbooru(), os.path.join(db_path, booru_name + ".txt"), prompts_file)
    elif booru_name == "Derpibooru":
        scraper = BooruScraper(booru.Derpibooru(), os.path.join(db_path, booru_name + ".txt"), prompts_file)
    elif booru_name == "E621":
        scraper = BooruScraper(booru.E621(), os.path.join(db_path, booru_name + ".txt"), prompts_file)
    elif booru_name == "E926":
        scraper = BooruScraper(booru.E926(), os.path.join(db_path, booru_name + ".txt"), prompts_file)
    elif booru_name == "Furbooru":
        scraper = BooruScraper(booru.Furbooru(), os.path.join(db_path, booru_name + ".txt"), prompts_file)
    elif booru_name == "Gelbooru":
        scraper = BooruScraper(booru.Gelbooru(), os.path.join(db_path, booru_name + ".txt"), prompts_file)
    elif booru_name == "Hypnohub":
        scraper = BooruScraper(booru.Hypnohub(), os.path.join(db_path, booru_name + ".txt"), prompts_file)
    elif booru_name == "Konachan":
        scraper = BooruScraper(booru.Konachan(), os.path.join(db_path, booru_name + ".txt"), prompts_file)
    elif booru_name == "Konachan_Net":
        scraper = BooruScraper(booru.Konachan_Net(), os.path.join(db_path, booru_name + ".txt"), prompts_file)
    elif booru_name == "Lolibooru":
        scraper = BooruScraper(booru.Lolibooru(), os.path.join(db_path, booru_name + ".txt"), prompts_file)
    elif booru_name == "Paheal":
        scraper = BooruScraper(booru.Paheal(), os.path.join(db_path, booru_name + ".txt"), prompts_file)
    elif booru_name == "Realbooru":
        scraper = BooruScraper(booru.Realbooru(), os.path.join(db_path, booru_name + ".txt"), prompts_file)
    elif booru_name == "Rule34":
        scraper = BooruScraper(booru.Rule34(), os.path.join(db_path, booru_name + ".txt"), prompts_file)
    elif booru_name == "Safebooru":
        scraper = BooruScraper(booru.Safebooru(), os.path.join(db_path, booru_name + ".txt"), prompts_file)
    elif booru_name == "Xbooru":
        scraper = BooruScraper(booru.Xbooru(), os.path.join(db_path, booru_name + ".txt"), prompts_file)
    elif booru_name == "Yandere":
        scraper = BooruScraper(booru.Yandere(), os.path.join(db_path, booru_name + ".txt"), prompts_file)
    else:
        print(booru_name + " is not supported")
        exit()
    scraper.start()
