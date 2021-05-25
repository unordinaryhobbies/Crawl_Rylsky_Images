from concurrent.futures import thread
from bs4 import BeautifulSoup
import requests
import os
import pdb
import concurrent.futures as cf
import time
from typing import List, Union

class GetRylskyModels():
    def __init__(self, html: str, model="models.txt"):
        self.GetMainHtml = requests.get(html)
        self.mainHTML = BeautifulSoup(self.GetMainHtml.content, 'lxml')
        self.modelHTMLs: List[str] = []
        self.redirectHTMLs: List[str] = []
        self.modelFile = model
    def __GetModelsHTML(self):
        ULs = self.mainHTML.find_all('ul',class_='gallery-a a d')
        info = []
        for ul in ULs:
            As = ul.find_all('a')
            for a in As:
                name = a.find_all('span')[-1].text
                # print(name)
                info = [name, a['href']]
                # print("{}\n\n".format(a['href']))
                self.modelHTMLs.append(info)
    def __ReadModels(self):
        with open(self.modelFile, 'r') as Read:
            for read in Read:
                info = Read.readline().split(',')
                # print("{}\n".format(info))
                self.redirectHTMLs.append(info)
        # print(self.redirectHTMLs)
    def __WriteModels(self):
        with open(self.modelFile,'a') as Write:
            for redirect in self.redirectHTMLs:
                Write.write("{},{}\n".format(redirect[0], redirect[1]))
    def __GetRedirectURL(self):
        for modelHTML in self.modelHTMLs:
            print("{}, {}\n".format(modelHTML[0], modelHTML[1]))
            # print("Reading {}th model's website".format(i))
            html = requests.get(modelHTML[1])
            HTML = BeautifulSoup(html.content, 'lxml')
            ULs = HTML.find_all('ul', class_ = 'gallery-a b')
            for ul in ULs:
                As = ul.find_all('a')
                # print(self.redirectHTMLs)
                # sleep(10)
                for a in As:
                    info = []
                    info.append(modelHTML[0])
                    info.append(a['href'])
                    # print("{}\n\n".format(info))
                    self.redirectHTMLs.append(info)
    @staticmethod
    def __GetImageTagsInImageHTML(redirectHTML: str) -> Union[List[str], None]:
        imageLink = []
        
        #Calling Model's Collection Album html
        html = requests.get(redirectHTML,timeout=5)
        content = BeautifulSoup(html.content, 'lxml')

        ul = content.find('ul', class_='list-gallery a css')
        try:
            #Find all image tags
            imageTags = ul.find_all('img')
        except Exception:
            return None
        #Append all the images and return
        for tag in imageTags:
            imageLink.append(tag)
        return imageLink
    def __GetImage(self, ImgLinks, dir: str) -> None:
      try:
        for i , img in enumerate(ImgLinks):
              
            #Replace blank space in title with '_'
            path = img['alt'].replace(' ','_')

            #Get the image file link
            RawImg = requests.get(img['src'], timeout=5)

            #Check if dir exist before copying image to the directory
            if os.path.isdir("{0}/{1}/{2}".format('pic',dir,path)) is False:
                os.mkdir("{0}/{1}/{2}".format('pic',dir,path))

            print("Downloading {:>90}: {:>15}th image".format(path, i))

            self.__WriteImage(path="{0}/{1}/{2}/{3}.jpg".format('pic',dir, path , path+str(i)), RawImage=RawImg)
      except Exception:
        pass
    
    #Write data to the image.
    @staticmethod
    def __WriteImage(path: str, RawImage):
          file = open(path, "wb")
          file.write(RawImage.content)
          file.close()

    def __DownloadImages(self,start=0):
      length = len(self.redirectHTMLs)
      i = 0
      try:
        #Call multi thread to process faster
        with cf.ThreadPoolExecutor() as worker:
          for i in range(start, length):
              worker.submit(self.__DownloadImage, i)

      except KeyboardInterrupt:
        exit()

      except Exception:
        self.__DownloadImages(i)
                      
    def __DownloadImage(self, index: int):
          redirect = self.redirectHTMLs[index]
          Tags = self.__GetImageTagsInImageHTML(redirect[1])

          #Model's name
          name = redirect[0]

          #Check if dir exist before writing getting model's pic
          if os.path.isdir("pic/{}".format(name)) is False:
                os.mkdir("pic/{}".format(name))

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

    @staticmethod
    def Timer(startedTime):
          time_elapsed = time.time() - startedTime
          
          hour, min_sec = divmod(time_elapsed, 3600)
          min, sec = divmod(min_sec, 60)
          print("{:>3} hour {:>3} minute {:>3} second".format(int(hour), int(min), int(sec)))
          
    def GetAllImages(self):
          start = time.time()
          try:
            self.__ReadModels()
            if os.path.isdir('pic') is False:
                os.mkdir('pic')
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
        self.__GetModelsHTML()
        print("reading model's html done")
        self.__GetRedirectURL()
        print("Collecting model's picture html files done")
        self.__WriteModels()

if __name__ == '__main__':
    html = "https://www.elitebabes.com/top-rated-babes/"
    Rylsky = GetRylskyModels(html)
    Rylsky.GetAllImages()