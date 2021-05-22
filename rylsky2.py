from bs4 import BeautifulSoup
import requests
import os
class GetRylskyModels():
    def __init__(self, html, model="models.txt"):
        self.GetMainHtml = requests.get(html)
        self.mainHTML = BeautifulSoup(self.GetMainHtml.content, 'lxml')
        self.modelHTMLs = []
        self.redirectHTMLs = []
        self.modelFile = model
    def GetModelsHTML(self):
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
    def ReadModels(self):
        with open(self.modelFile, 'r') as Read:
            for read in Read:
                info = Read.readline().split(',')
                # print("{}\n".format(info))
                self.redirectHTMLs.append(info)
        # print(self.redirectHTMLs)
    def WriteModels(self):
        with open(self.modelFile,'a') as Write:
            for redirect in self.redirectHTMLs:
                Write.write("{},{}\n".format(redirect[0], redirect[1]))
    def GetRedirectURL(self):
        i = 0
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

    def GetImageTagsInImageHTML(self, redirectHTML):
        imageLink = []
        print(redirectHTML)
        html = requests.get(redirectHTML,timeout=5)
        content = BeautifulSoup(html.content, 'lxml')
        ul = content.find('ul', class_='list-gallery a css')
        try:
            imageTags = ul.find_all('img')
        except Exception:
            return
        for tag in imageTags:
            imageLink.append(tag)
        return imageLink

    def GetImg(self, ImgLinks, dir):
      try:
        for i in range(len(ImgLinks)):
            img = ImgLinks[i]
            path = img['alt'].replace(' ','_')
            RawImg = requests.get(img['src'], timeout=5)
            if os.path.isdir("{0}/{1}".format(dir,path)) is False:
                os.mkdir("{0}/{1}".format(dir,path))
            print("downloading {}: {}th image".format(path, i))
            file = open("{0}/{1}/{2}.jpg".format(dir, path , path+str(i)), "wb")
            file.write(RawImg.content)
<<<<<<< HEAD
            file.close()
      except Exception:
        pass
    def DownloadImages(self,start=0):
      length = len(self.redirectHTMLs)
      try:
        for i in range(start, length):
            redirect = self.redirectHTMLs[i]
            Tags = self.GetImageTagsInImageHTML(redirect[1])
            name = redirect[0]
            if os.path.isdir(name) == False:
                os.mkdir(name)
            self.GetImg(Tags, name)
      except Exception:
=======
            file.close()
      except Exception:
        pass
    def DownloadImages(self,start=0):
      length = len(self.redirectHTMLs)
      try:
        for i in range(start, length):
            redirect = self.redirectHTMLs[i]
            Tags = self.GetImageTagsInImageHTML(redirect[1])
            name = redirect[0]
            if os.path.isdir(name) is False:
                os.mkdir(name)
            self.GetImg(Tags, name)
      except Exception:
>>>>>>> 2d2436894ffee0f63afe15c15c0bce1c3ec8f2d4
        self.DownloadImages(i)
    def Run(self):
        # self.GetModelsHTML()
        # print("reading model's html done")
        # self.GetRedirectURL()
        # print("Collecting model's picture html files done")
        # self.WriteModels()
        self.ReadModels()
        self.DownloadImages()
