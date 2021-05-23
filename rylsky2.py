from bs4 import BeautifulSoup
import requests
import os
import asyncio
import pdb

class GetRylskyModels():
    def __init__(self, html, model="models.txt"):
        self.GetMainHtml = requests.get(html)
        self.mainHTML = BeautifulSoup(self.GetMainHtml.content, 'lxml')
        self.modelHTMLs = []
        self.redirectHTMLs = []
        self.modelFile = model
    def __GetModelsHTML(self):
        ULs = self.mainHTML.find_all('ul',class_='gallery-a a d')
        info = []
        for ul in ULs:
            As = ul.find_all('a')
            # print("-------------------------------------------------------------")
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
    def GetRedirectURL(self):
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
    def GetImageTagsInImageHTML(redirectHTML):
        imageLink = []
        
        #Calling Model's Collection Album html
        html = requests.get(redirectHTML,timeout=5)
        content = BeautifulSoup(html.content, 'lxml')

        ul = content.find('ul', class_='list-gallery a css')
        try:
            #Find all image tags
            imageTags = ul.find_all('img')
        except Exception:
            return
        #Append all the images and return
        for tag in imageTags:
            imageLink.append(tag)
        return imageLink
    def __GetImage(self, ImgLinks, dir):
      try:
        for i in range(len(ImgLinks)):
            #Image tag from html file
            img = ImgLinks[i]

            #Replace blank space in title with '_'
            path = img['alt'].replace(' ','_')

            #Get the image file link
            RawImg = requests.get(img['src'], timeout=5)

            #Check if dir exist before copying image to the directory
            if os.path.isdir("{0}/{1}/{2}".format('pic',dir,path)) is False:
                os.mkdir("{0}/{1}/{2}".format('pic',dir,path))

            print("downloading {}: {}th image".format(path, i))

            self.__WriteImage(path="{0}/{1}/{2}/{3}.jpg".format('pic',dir, path , path+str(i)), RawImage=RawImg)
      except Exception:
        pass
    
    #Write data to the image.
    @staticmethod
    def __WriteImage(path, RawImage):
          file = open(path, "wb")
          file.write(RawImage.content)
          file.close()

    def __DownloadImages(self,start=0):
      length = len(self.redirectHTMLs)
      try:
        for i in range(start, length, 4):
            print("Recording {}th out of {}\n{}%\n\n".format(i,length,(i/length *100)))
            self.__DownloadImage(i)
      except Exception:
        self.__DownloadImages(i)
    def __DownloadImage(self, index):
          redirect = self.redirectHTMLs[index]
          Tags = self.GetImageTagsInImageHTML(redirect[1])

          #Model's name
          name = redirect[0]

          #Check if dir exist before writing getting model's pic
          if os.path.isdir("pic/{}".format(name)) == False:
                os.mkdir("pic/{}".format(name))

          #Call images from the website
          self.__GetImage(Tags, name)

          #Record the last section so that if the network fails, it will remember it's last reading
          self.__RecordLastSection(str(index))
    #Record lsat section of writing image
    @staticmethod
    def __RecordLastSection(lastsection):
      file = open('lastsection.txt','w')
      file.write(lastsection)
      file.close()
    #Read last section of writing image
    @staticmethod
    def __ReadLastSection():
      try:
        with open("lastsection.txt",'r') as r:
          last = r.readline()
          last = int(last)
        return last
      except FileNotFoundError:
        return
      except ValueError:
        return
    def Run(self):
        # self.__GetModelsHTML()
        # print("reading model's html done")
        # self.GetRedirectURL()
        # print("Collecting model's picture html files done")
        # self.__WriteModels()
        self.__ReadModels()
        if os.path.isdir('pic') == False:
            os.mkdir('pic')
        lastRead =self.__ReadLastSection()
        if lastRead != None:
          self.__DownloadImages(lastRead)
        else:
          self.__DownloadImages()

if __name__ == '__main__':
    html = "https://www.elitebabes.com/top-rated-babes/"
    Rylsky = GetRylskyModels(html)
    Rylsky.Run()