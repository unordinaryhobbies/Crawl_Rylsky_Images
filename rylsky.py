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
#2.Run Rylsky.ProcessLinksBeforeDownload() to get all the model's album links. (This process take approximately 17 - 21 minutes)
#3.After getting all the model album links, Run Rylsky.DownloadAllImages() to download all images

#How it produces a folder
##########################################
#When it starts to download the image, 
#At the top, it will produce a folder called "RylskyTopModels"
#then it will produce folders according to the model's name
#Each model folder contains their albums and have photos in it

#Information about rylsky hot models page
##########################################
#In total the page has 90000+ links
#It has 42025 folders
#It is 31.1 GB in total
#There are approximately 100+ pages in rylsky top models
#There are 89 model profiles in rylsky top model page 1
#One Model Profile contains approximately 10-100 albums
#One Model Album contains approximately 10-20 pictures
#In total, it downloads approximately 614 thousand pictures
#It takes 9 hours 23 minutes to download all the files

from bs4 import BeautifulSoup
import requests
import os
import pdb
import concurrent.futures as cf
import sys
import time
from typing import List, Union, Callable

class GetRylskyModels():
    def __init__(self, ModelProfileLinkDatabase="ModelAlbumLinks.txt"):
        self.RylskyHotModelMainPage = "https://www.elitebabes.com/top-rated-babes/"
        self.__ModelProfileLinks: List[str] = []
        self.ModelNameAndAlbumLinks: List[str] = []
        self.__ModelProfileLinkDatabase = ModelProfileLinkDatabase
        self.__HotModelPages: List[str] = ["https://www.elitebabes.com/top-rated-babes/"]
    
    def __GetHotModelPages(self, NextPage: str, MaxPageLimit = 50):
        
        #If it reached more than the max limit, exit
        if str(MaxPageLimit) in NextPage:
              return None

        #Get next page
        HotModelPage = requests.get(NextPage)
        HotModelPage = BeautifulSoup(HotModelPage.content, 'lxml')

        Nav_HotModelPage = HotModelPage.find('nav', class_='pagination-a')

        Li_NextPage = Nav_HotModelPage.find('li', class_='next')
        
        #Repeat until there are no next pages
        if Li_NextPage is not None:
          NextHotModelPageLink = Li_NextPage.find('a')['href']
          print("Found : {}".format(NextHotModelPageLink))

          self.__HotModelPages.append(NextHotModelPageLink)

          return self.__GetHotModelPages(NextHotModelPageLink)
        
        return None

    #Get model's profile links to get model's album links
    def __GetModelProfileLinks(self):
          
        for HotModelPage in self.__HotModelPages:
          #Get Request From Each Page
          HotModelPage = requests.get(HotModelPage)
          HotModelPage = BeautifulSoup(HotModelPage.content, 'lxml')
          #Call unordered list that stores the model's profile
          ULs = HotModelPage.find_all('ul', class_='gallery-a a d')

          ModelProfileLink = []

          #Store model's name and profile link in list
          for ul in ULs:
            #Find model's link by finding a href link
            As = ul.find_all('a')

            with cf.ThreadPoolExecutor() as worker:
              for a in As:
                  #Get the <span> which contains the name of the model
                  name = a.find_all('span')[-1].text
                  print("\nTarget: Model name found! : {}".format(name))

                  ModelProfileLink = [name, a['href']]
                  worker.submit(self.FindAdditionalModelProfileLinks, ModelProfileLink)

    def FindAdditionalModelProfileLinks(self, ModelProfileLink):
        self.__ModelProfileLinks.append(ModelProfileLink)

        #Check if model profile's additional pages exist and append them
        self.__CheckAdditionalPagesInModelProfileExist(ModelProfileLink)
    
    def __ReadModelProfileLinkDB(self):
        self.ModelNameAndAlbumLinks = []
        with open(self.__ModelProfileLinkDatabase, 'r') as Read:
            for read in Read:
                info = Read.readline().split(',')

                self.ModelNameAndAlbumLinks.append(info)

    def __WriteModelProfileLinkDB(self):
        self.__ModelProfileLinks.sort(key=lambda ModelProfileLink: ModelProfileLink[0],reverse=True)
        with open(self.__ModelProfileLinkDatabase,'a') as Write:
            for redirect in self.ModelNameAndAlbumLinks:
                Write.write("{},{}\n".format(redirect[0], redirect[1]))

    def __CheckAdditionalPagesInModelProfileExist(self, ModelProfileLink):
          Name, ProfileLink = ModelProfileLink

          #Get model's profile's HTML
          ModelProfile = requests.get(ProfileLink)
          ModelProfile = BeautifulSoup(ModelProfile.content, "lxml")
          
          #Find if additional pages exist
          AdditionalPages = ModelProfile.find("div", class_="m-pagination")

          #If there are no additional pages, exit
          if AdditionalPages is None:
                print("No additional pages found")
                return
          #Otherwise, find "a" element
          AdditionalPagesSource = AdditionalPages.find_all('a')

          for ModelProfileLink in AdditionalPagesSource:
                #Check if the link is relevent to models
                if ModelProfileLink['href'].startswith('https://www.elitebabes.com/model') and 'mpage' in ModelProfileLink['href']:
                  ModelProfile = [Name, ModelProfileLink['href']]
                  print("Model Profile links Found!: {}".format(ModelProfile[1]))
                  self.__ModelProfileLinks.append(ModelProfile)
    
    def __GetModelAlbumLinks(self):
          with cf.ThreadPoolExecutor() as worker:
            for Name, ModelProfileLink in self.__ModelProfileLinks:
                  worker.submit(self.__GetModelAlbumLink, Name, ModelProfileLink)
                

    def __GetModelAlbumLink(self, Name, ModelProfileLink):
          #Get the model's profile HTML source  
          ModelProfile = requests.get(ModelProfileLink)
          ModelProfile = BeautifulSoup(ModelProfile.content, 'lxml')

          ULs = ModelProfile.find_all('ul', class_ = 'gallery-a b')

          #From model's profile link, search for all the model's albums
          for ul in ULs:
              #Find model's album links
              As = ul.find_all('a')

              for a in As:
                  ModelNameAndAlbumLink = []

                  #Name of the model
                  ModelNameAndAlbumLink.append(Name)
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

    def __GetImage(self, ImgLinks, directory: str):
      try:
        for i , img in enumerate(ImgLinks):
              
            #Replace blank space in title with '_'
            path = img['alt'].replace(' ','_')

            #Get the image file link
            RawImg = requests.get(img['src'], timeout=5)

            #Check if dir exist before copying image to the directory
            if os.path.isdir("{0}/{1}/{2}".format('RylskyTopModels',directory,path)) is False:
                os.mkdir("{0}/{1}/{2}".format('RylskyTopModels',directory,path))

            print("Downloading {:>90}: {:>15}th image".format(path, i))

            self.__WriteImage(path="{0}/{1}/{2}/{3}.jpg".format('RylskyTopModels',directory, path , path+str(i)), RawImage=RawImg)
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
          
          hours, min_sec = divmod(time_elapsed, 3600)
          minutes, seconds = divmod(min_sec, 60)
          print("{:>3} hour {:>3} minute {:>3} second".format(int(hours), int(minutes), int(seconds)))

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
        start = time.time()
        print("Running...")
        self.__GetHotModelPages(self.RylskyHotModelMainPage)
        
        self.__GetModelProfileLinks()
        print("\n\nFetching Model's Profile done!\n\n")
        self.__GetModelAlbumLinks()
        print("\n\nFetching Model's List of Albums done!\n\n")
        self.__WriteModelProfileLinkDB()
        print("\n\nWriting To ModelAlbumLink Done\n\n")
        self.Timer(start)

if __name__ == '__main__':
    Rylsky = GetRylskyModels()
    # Rylsky.ProcessLinksBeforeDownload()
    Rylsky.DownloadAllImages()