from typing import List, Dict
from abc import ABC, abstractmethod
from time import time

#WARNING NSFW!
class CrawlingNudeLinks(ABC):
    async def __Fetch_Websites_Source(self, ModelInfoAndLinks: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Fetch all the model album website source from given model list dictionary
        use background concurrent task to increase speed
        """
        raise NotImplementedError("You must fetch website source in order to crawl")

    @abstractmethod
    async def _GetMainPageSource(self) -> None:
        """
        Go to
        Main website
        then fetch models link and store it in self list

        1.Convert it into bs4 object
        2.Get ul element -> list for model html paths
        3.Extract all 'a href' & 'img alt'
        4.Record it in self.model_pages list
        """
        raise NotImplementedError("You have to have main page source")

    @abstractmethod
    async def _GetAllAlbumPageFromModelPage(self) -> None:
        """
        Go to all the models page saved in self.model_pages then
        fetch model's album link
        model link ex: 'https://www.elitebabes.com/model/alisa-i/'

        1.Convert it into bs4 object
        2.Get ul element -> list for model html paths
        3.Extract all 'a href' path
        4.Record it in self list
        """

        pass

    @abstractmethod
    async def FindAllImagesInAlbum(self) -> None:
        """
        Inside self.model_albums, there are all the links to the model albums
        Now we are going to go inside to all the album links then get all the <a href> element of the images
        Store it in dict(model name, name album, picture link) format
        Album Link Example: https://www.elitebabes.com/sweet-and-charming-stuns-us-with-her-sexy-legs-and-shaved-pussy-17116/
        """
        raise NotImplementedError("You have to crawl images from album!")

    @abstractmethod
    def WriteAlbumLinkToTxtFile(self) -> None:
        """
        Write the album image links(which is in the self.picture_pages list) to the given txt file
        Writing procedure:
            Delimiter: ;
            1. name of the model
            2. name of the album
            3. picture link
        """
        raise NotImplementedError("You have to write the image links to the file")

    async def run(self) -> None:
        """
        Main function of this object
        Handles all the download process
        """
        start = time()
        await self._GetMainPageSource()
        try:
            await self._GetAllAlbumPageFromModelPage()
        except NotImplementedError:
            print('WARNING: YOU DID NOT IMPLEMENT _GetAllAlbumPageFromModelPage function.')
        await self.FindAllImagesInAlbum()
        self.WriteAlbumLinkToTxtFile()
        print(f"Time Taken = {(time() - start):.2f} s", end='\r')