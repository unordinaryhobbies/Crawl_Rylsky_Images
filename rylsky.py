#Program informations

#What this program does?
##########################################
#Get pictures of top rated rylsky model in page 1

#Algorithm
##########################################
#Get Models profile link -> Get List of model's album links-> Get Album's picture links-> Download the picture's link

#How to Run?
##########################################
#1.Initialise Constructor
#2.Run Rylsky.ProcessLinksBeforeDownload() to get all the model's album links
#3.After getting all the model album links, Run Rylsky.DownloadAllImages() to download all images

#How it produces a folder
##########################################
#When it starts to download the image, 
#At the top, it will produce a folder called "RylskyTopModels"
#then it will produce folders according to the model's name
#Each model folder contains their albums and have photos in it

#Information about rylsky hot models page
##########################################
#There are 89 model profiles in rylsky top model page 1
#One Model Profile contains approximately 10-50 albums
#One Model Album contains approximately 10-20 pictures
#In total, it downloads approximately 50 thousand pictures

from concurrent.futures import thread
from bs4 import BeautifulSoup
import requests
import os
import pdb
import concurrent.futures as cf
import sys
import time
from typing import List, Union

class GetRylskyModels():
    def __init__(self, ModelProfileLinkDatabase="ModelAlbumLinks.txt"):
        self.RylskyHotModelPage = "https://www.elitebabes.com/top-rated-babes/"
        self.__ModelProfileLinks: List[str] = []
        self.ModelNameAndAlbumLinks: List[str] = []
        self.__ModelProfileLinkDatabase = ModelProfileLinkDatabase

    #Call main html and convert to BS4 type
    def __GetHotModelPage(self):
        #Get the main html
        RylskyMainHTML = requests.get(self.RylskyHotModelPage)

        #When main html is received process it with bs4
        self.__RylskyMainHTML: str = BeautifulSoup(RylskyMainHTML.content, 'lxml')

    #Get model's profile links to get model's album links
    def __GetModelProfileLinks(self):
        #Call unordered list that stores the model's profile
        ULs = self.__RylskyMainHTML.find_all('ul', class_='gallery-a a d')

        #
        ModelProfileLink = []

        #Store model's name and profile link in list
        for ul in ULs:
            #Find model's link by finding a href link
            As = ul.find_all('a')

            for a in As:
                #Get the <span> which contains the name of the model
                name = a.find_all('span')[-1].text
                print("Target: Model name found! : {}".format(name))

                ModelProfileLink = [name, a['href']]

                self.__ModelProfileLinks.append(ModelProfileLink)
    
    def __ReadModelProfileLinkDB(self):
        with open(self.__ModelProfileLinkDatabase, 'r') as Read:
            for read in Read:
                info = Read.readline().split(',')

                self.ModelNameAndAlbumLinks.append(info)

    def __WriteModelProfileLinkDB(self):
        with open(self.__ModelProfileLinkDatabase,'a') as Write:
            for redirect in self.ModelNameAndAlbumLinks:
                Write.write("{},{}\n".format(redirect[0], redirect[1]))

    def __GetModelAlbumLinks(self):
        for ModelProfileLink in self.__ModelProfileLinks:
            #Get the model's profile HTML source  
            ModelProfile = requests.get(ModelProfileLink[1])
            ModelProfile = BeautifulSoup(ModelProfile.content, 'lxml')

            ULs = ModelProfile.find_all('ul', class_ = 'gallery-a b')

            #From model's profile link, search for all the model's albums
            for ul in ULs:
                #Find model's album links
                As = ul.find_all('a')

                for a in As:
                    ModelNameAndAlbumLink = []

                    #Name of the model
                    ModelNameAndAlbumLink.append(ModelProfileLink[0])
                    #Model's album link
                    ModelNameAndAlbumLink.append(a['href'])

                    print("Model Album Found!: {}".format(ModelNameAndAlbumLink[1]))

                    self.ModelNameAndAlbumLinks.append(ModelNameAndAlbumLink)

    @staticmethod
    def __GetImageTagsInImageHTML(ModelAlbumLink: str) -> Union[List[str], None]:
        AlbumImgTags: List[str] = []
        
        #Calling Model's Album Link
        ModelAlbumLink = requests.get(ModelAlbumLink,timeout=5)
        content = BeautifulSoup(ModelAlbumLink.content, 'lxml')

        ul = content.find('ul', class_='list-gallery a css')

        #Find all image tags
        try:
            ModelAlbumImageTags = ul.find_all('img')
        #If none of the img tags are found, return nothing
        except Exception:
            return None

        #Append all the image tags and return the list of <img> tags
        for ModelAlbumImageTag in ModelAlbumImageTags:
            AlbumImgTags.append(ModelAlbumImageTag)
        return AlbumImgTags

    def __GetImage(self, ImgLinks, dir: str):
      try:
        for i , img in enumerate(ImgLinks):
              
            #Replace blank space in title with '_'
            path = img['alt'].replace(' ','_')

            #Get the image file link
            RawImg = requests.get(img['src'], timeout=5)

            #Check if dir exist before copying image to the directory
            if os.path.isdir("{0}/{1}/{2}".format('RylskyTopModels',dir,path)) is False:
                os.mkdir("{0}/{1}/{2}".format('RylskyTopModels',dir,path))

            print("Downloading {:>90}: {:>15}th image".format(path, i))

            self.__WriteImage(path="{0}/{1}/{2}/{3}.jpg".format('RylskyTopModels',dir, path , path+str(i)), RawImage=RawImg)
      except Exception:
        pass
    
    #Write data to the image.
    @staticmethod
    def __WriteImage(path: str, RawImage):
          file = open(path, "wb")
          file.write(RawImage.content)
          file.close()

    def __DownloadImages(self,start=0):
      length = len(self.ModelNameAndAlbumLinks)
      i = 0
      try:
        #Call multi thread to process faster
        with cf.ThreadPoolExecutor() as worker:
          for i in range(start, length):
              worker.submit(self.__DownloadImage, i)

      except KeyboardInterrupt:
        sys.exit()

      except Exception:
        self.__DownloadImages(i)
                      
    def __DownloadImage(self, index: int):
          redirect = self.ModelNameAndAlbumLinks[index]
          Tags = self.__GetImageTagsInImageHTML(redirect[1])

          #Model's name
          name = redirect[0]

          #Check if dir exist before writing getting model's RylskyTopModels
          if os.path.isdir("RylskyTopModels/{}".format(name)) is False:
                os.mkdir("RylskyTopModels/{}".format(name))

          #Call images from the website
          self.__GetImage(Tags, name)

          #Record the last section so that if the network fails, it will remember it's last reading
          #Potential problem collision with recording
          # self.__RecordLastSection(str(index))

    #Record lsat section of writing image
    @staticmethod
    def __RecordLastSection(lastsection: str):
      file = open('lastsection.txt','w')
      file.write(lastsection)
      file.close()
    #Read last section of writing image
    @staticmethod
    def __ReadLastSection() -> Union[int, None]:
      try:
        with open("lastsection.txt",'r') as r:
          last: int = int(r.readline())

        #If value found, return the last recorded value
        return last

      except FileNotFoundError:
        return None

    #Used to calculate total time taken to download all file
    @staticmethod
    def Timer(startedTime):
          time_elapsed = time.time() - startedTime
          
          hour, min_sec = divmod(time_elapsed, 3600)
          min, sec = divmod(min_sec, 60)
          print("{:>3} hour {:>3} minute {:>3} second".format(int(hour), int(min), int(sec)))

    def DownloadAllImages(self):
          start = time.time()
          try:
            self.__ReadModelProfileLinkDB()
            if os.path.isdir('RylskyTopModels') is False:
                os.mkdir('RylskyTopModels')
            lastRead = self.__ReadLastSection()
            if lastRead is not None:
              self.__DownloadImages(lastRead)
            else:
              self.__DownloadImages()

            #Print time elapsed
            self.Timer(start)
            
          except KeyboardInterrupt:
            pass

    def ProcessLinksBeforeDownload(self):
        print("Running...")
        self.__GetHotModelPage()
        self.__GetModelProfileLinks()
        print("\n\nFetching Model's Profile done!\n\n")
        self.__GetModelAlbumLinks()
        print("\n\nFetching Model's List of Albums done!\n\n")
        self.__WriteModelProfileLinkDB()
        print("\n\nWriting To ModelAlbumLink Done\n\n")

if __name__ == '__main__':
    Rylsky = GetRylskyModels()
    Rylsky.ProcessLinksBeforeDownload()
    # Rylsky.DownloadAllImages()