import aiohttp
from bs4 import BeautifulSoup # type: ignore
from typing import List, Any, Dict, Optional
import asyncio
from time import time
import os

#WARNING NSFW!
class RylSkyImageLinkFinder:
    """
    Rylsky images link finding and recording code
    Take 15 - 60 second to get image paths.
    """
    def __init__(self, TargetMainPage: int = 1, WriteMode: str = 'w', AlbumTxtPath: str = 'ModelAlbumLinks.txt') -> None:
        #model websites links
        self.model_webs: List[str] = []
        self.main_page: str = "https://www.elitebabes.com/top-rated-babes/page/"
        self.album_file: str = AlbumTxtPath
        self.model_pages: List[Dict[str, str]] = []
        self.model_albums: List[Dict[str, Any]] = []
        self.picture_pages: List[Dict[str, str]] = []
        self.main_page_num: int = TargetMainPage
        self.writeMode: str = WriteMode

    @staticmethod
    async def __Fetch_Website_Source(ModelDict: Dict[str, str]) -> Dict[str, Optional[str]]:
        """
        Fetch all the model album websites source from given model dictionary
        return value:
            1st: website source
            2nd: model name
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(ModelDict['link']) as response:
                return dict([('source', await response.text()), ('name', ModelDict['name']), ('album', ModelDict.get('album'))])

    async def __Fetch_Websites_Source(self, ModelInfoAndLinks: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Fetch all the model album website source from given model list dictionary
        use background task to increase speed
        """
        tasks = list(map(lambda link: asyncio.create_task(self.__Fetch_Website_Source(link)), ModelInfoAndLinks))
        return await asyncio.gather(*tasks)

    async def _GetMainPageSource(self) -> Any:
        """
        Go to
        https://www.elitebabes.com/top-rated-babes/
        And fetch models link

        1.Convert it into bs4 object
        2.Get ul element -> list for model html paths
        3.Extract all 'a href' & 'img alt'
        4.Record it in self.model_pages list
        """

        async with aiohttp.ClientSession() as session:
            async with session.get(self.main_page + str(self.main_page_num)) as main_web:
                website_source = BeautifulSoup(await main_web.text(), 'lxml')
                model_ul = website_source.find('ul', class_='gallery-a a d')
                model_li = model_ul.find_all('a')
                self.model_pages.extend(list(map(lambda a: {'link': a['href'], 'name': a.find('img')['alt']}, model_li)))
        return self

    async def _GetAllAlbumPageFromModelPage(self) -> Any:
        """
        Go to all the models page saved in self.model_pages then
        fetch model's album link
        model link ex: 'https://www.elitebabes.com/model/alisa-i/'

        1.Convert it into bs4 object
        2.Get ul element -> list for model html paths
        3.Extract all 'a href' path
        4.Record it in self.model_albums list
        """

        model_web = await self.__Fetch_Websites_Source(self.model_pages)

        """
        Process the raw html files
        1. find ul element to extract the model albums
        2. find all <a href> element to get the redirect links 
        """
        for model in model_web:
            website_source = BeautifulSoup(model['source'], 'lxml')
            album_ul = website_source.find('ul', class_='gallery-a b')
            album_li = album_ul.find_all('li')
            self.model_albums.extend(list(map(\
                lambda link: dict([('link', link.find('a')['href']), ('name', model['name']), ('album', link.find('img')['alt'])]),\
                     album_li)))
        return self

    async def FindAllImagesInAlbum(self) -> Any:
        """
        Inside self.model_albums, there are all the links to the model albums
        Now we are going to go inside to all the album links then get all the <a href> for the image
        Album Link Example: https://www.elitebabes.com/sweet-and-charming-stuns-us-with-her-sexy-legs-and-shaved-pussy-17116/
        """
        album_web = await self.__Fetch_Websites_Source(self.model_albums)
        """
        Process the raw html files
        1. find ul element to extract the model albums
        2. find all <a href> image elements 
        """
        for album in album_web:
            website_source = BeautifulSoup(album['source'], 'lxml')
            album_ul = website_source.find('ul', class_='list-gallery a css')
            try:
                album_li = album_ul.find_all('a')
                self.picture_pages.extend(list(map(lambda web: {'name': album['name'], 'link': web['href'], 'album': album['album']}, album_li)))
            except AttributeError:
                pass
        return self

    def WriteAlbumLinkToTxtFile(self):
        """
        Write the album image links(which is in the self.picture_pages list) to the given txt file
        Writing procedure:
            Delimiter: ;
            1. name of the model
            2. name of the album
            3. picture link
        """
        with open(self.album_file, mode=self.writeMode, encoding='UTF-8') as f:
            for pic_info in self.picture_pages:
                try:
                    f.write(f"{pic_info['name']};{pic_info['album']};{pic_info['link']}\n")
                except UnicodeEncodeError:
                    pass

    async def run(self):
        """
        Main function of this object
        Handles all the download process
        """
        start = time()
        await self._GetMainPageSource()
        print(f"Getting MainPage: {time() - start:.2f} second taken")
        await self._GetAllAlbumPageFromModelPage()
        print(f"Getting AlbumsPage: {time() - start:.2f} second taken")
        await self.FindAllImagesInAlbum()
        print(f"Getting AlbumPhotoLinksPage: {time() - start:.2f} second taken")
        self.WriteAlbumLinkToTxtFile()
        print(f"Writing AlbumLinkToTxtFile: {time() - start:.2f} second taken")


class RylskyImageDownloader:
    def __init__(self, AlbumTxtPath = 'ModelAlbumLinks.txt'):
        self.index: int = 0
        self.album_file: str = AlbumTxtPath
        self.album_links: List[Dict[str, str]] = []
        self.sources: List[Dict[str, str]] = []
        self.finished_download: bool = False

    def _ReadTxtFile(self):
        """
        Read the file from self.album_file to get the album picture links
        then save the record in self.album_links
        """
        with open(self.album_file, mode='r') as file:
            model_name, album_name, link = file.readline().replace('\n', '').split(sep=',')
            self.album_links.append({'name': model_name, 'album': album_name, 'link': link})

        return self

    async def _DownloadSource(self, album_info: Dict[str, str]):
        """
        Download the image and pack it into dictionary formats
        return value:
            dictionary -> source: image source,
                            album: name of the album
                            name: name of the model
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(album_info['link']) as response:
                return {'source': response.content, 'name': album_info['name'], 'album': album_info['album']}

    async def _DownloadMultipleSource(self, DownloadLimitPerTime: int = 20):
        """
        1. Check if Download limit exceed
        2. Download source in background to increase efficiency
        3. Everytime when source is downloaded, increase self.index by 1
        4. Add the image sources to the self.sources
        """
        tasks: List[asyncio.Task] = []
        for _ in range(DownloadLimitPerTime):
            if self.index >= len(self.album_links):
                self.finished_download = True
                break
            tasks.append(asyncio.create_task(self._DownloadSource(self.album_links[self.index])))
            self.index += 1

        self.sources.extend(await asyncio.gather(*tasks))

        return self

    @staticmethod
    def _ConvertSourceToFile(Source: Any, ImagePath: str) -> None:
        """
        Get downloaded source and convert it into jpg or png file        
        """
        with open(ImagePath, 'w') as w:
            w.write(Source)

    @staticmethod
    def _CheckPathExistAndMakeFolder(ModelName: str, AlbumName: str) -> str:
        """
        Input model name and album name
        Make folder path in "model_name/album_name/picture_path" way
        """
        Path = os.path.join(ModelName, AlbumName)
        if os.path.exists(Path) is False:
            os.makedirs(Path)
        return Path

############################################
    async def Run(self):
        """
        Procedure:
            1. ReadTxtFile
            2. Check if folder exist if not make a new folder
            2. Repeat downloading and injecting source to the images
        """
        self._ReadTxtFile()
        while self.finished_download is False:
            print(f"Current Stage: {self.index} / {len(self.album_links)}... {self.index/ len(self.album_links) * 100:.2f} %")
            await self._DownloadMultipleSource()
            for index, source in enumerate(self.sources):
                Folders_Location = self._CheckPathExistAndMakeFolder(source['name'], source['album'])
                ##########################################
                #       PROBLEM:                         # 
                #       Image naming problem             #
                #       What to do?                      #
                ##########################################
                self._ConvertSourceToFile(source['source'], os.path.join(Folders_Location, str(index)+'.jpg'))
            del self.sources
###############################################

if __name__ == '__main__':
    start = time()
    test_finder = RylSkyImageLinkFinder(WriteMode='w')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_finder.run())
    print(f"{time() - start:.2f} second taken!")
    for i in range(2, 101):
        try:
            print(f"{i} th page writing...")
            test_finder = RylSkyImageLinkFinder(TargetMainPage=i, WriteMode='a')
            loop = asyncio.get_event_loop()
            loop.run_until_complete(test_finder.run())
        except Exception:
            print('UnicodeError: passing this stage')
            pass
    print(f"{time() - start:.2f} second taken!")
    # test_downloader = RylskyImageDownloader()
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(test_downloader.Run())