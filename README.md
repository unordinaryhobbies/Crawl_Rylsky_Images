# Crawl Rylsky Images

## What it does?
**⚠️Warning: Not Safe For Work**<br><br>
Program that scrap photos of nude art from [rylsky](https://www.elitebabes.com/)

## How it works?
1. Initially, It scapes all the pages available in the Rylsky main webpage. Then it finds all the models from the main pages. Inside the model page, there is a model's album that contains images of the model picture.<br>
2. The bot fetches all the available picture links and saves them in the `ModelAlbumLinks.txt` file.<br>
3. After the bot fetched all the picture links and stored them in the text file, it will download all the pictures asynchronously.<br>

**Crawling the picture links took approx 5-10 min in 20 Mbps (400000 - 500000 pictures)**<br>
**Downloading pictures took 2 - 3 hrs in 20 Mbps (20 GB)**

## How to run?
run this code in main to get all the picture links
```python
test_finder = RylSkyImagesLinkFinder()
test_finder.run()
```
then run this code in main to download all the images
```python
test_downloader = RylskyImageDownloader(DefaultDownloadPath='RylskyImages', InOneFile=False)
loop = asyncio.get_event_loop()
loop.run_until_complete(test_downloader.Run())
```
