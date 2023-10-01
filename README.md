# autotrainer
## How to use
### Setup environment
To start any of scripts you need to prepare venv environment. To setup environment, run either `setup-env.sh` or `setup-env-windows.sh`

### Image scraping
To start with image scraping, paste your tags separated by ',' in `prompts.txt` file.
At the start of each line specify how many images should be downloaded per iteration.

To start scraping images, run any of scraper .sh file.
You can also specify other booru scrapers by calling
`python scripts/autoscraper.py "YourScraperName"`

List of available scrapers are visible in `autoscraper.py` file

Your images should start to appear in `images/download` folder.

### Image aesthetic classification
To filter out ugly images, use `start-aesthetic-classifier.sh` script
Your images will now be moved from `images/download folder` to `images/aesthetic` folder if they are aesthetic enough.

To change aesthetic treshold, change either `anime_aesthetic_pass_treshold` or `cafeai_pass_treshold` (available values are from 0.0 to 1.0)
The higher value, the more aesthetic image will be.

If you don't want to delete unaesthetic files, then change `trash_folder = None` to `trash_folder = your/directory/here` in `aesthetic.py` file.
After that change unaesthetic file will be moved to specified folder instead of being deleted.

Check out https://huggingface.co/spaces/skytnt/anime-aesthetic-predict
This models is working good for filtering out ugly images

and https://huggingface.co/spaces/cafeai/cafe_aesthetic_demo
Which works great in removing images with high amout of text (like author name, comics, speech bubbles)

By changing `anime_aesthetic_quality_tresholds` in `aesthetic.py` file, you can change ranges for quality tags. If score is within range, corresponding quality tag will be added to caret file.

### Image tagging
To tag files, use `start-tagger.sh` script.
Your images now will be moved from  `images/aesthetic` to `images/tagged` folder.
If they are having blacklisted tags, they will be removed.

To change blacklisted tags, edit `blacklist` variable in `autotagger.py` file.

If you don't want to delete files with blacklisted tags, then change `trash_folder = None` to `trash_folder = your/directory/here` in `autotagger.py` file.

By increasing `min_tag_treshold` in `autotagger.py` file, only tags whcich taggers are more confident will be added to caret file.

By changing `default_tag_weight` in `autotagger.py` file, you will change default weights which are assigned for tags received from booru scrapers.

`autotagger.py` is adding weights from all taggers and tags from booru and then keeping only ones which have score higher than `min_tag_treshold`


