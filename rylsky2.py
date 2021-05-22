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
            if os.path.isdir("{0}/{1}/{2}".format('pic',dir,path)) is False:
                os.mkdir("{0}/{1}/{2}".format('pic',dir,path))
            print("downloading {}: {}th image".format(path, i))
            file = open("{0}/{1}/{2}/{3}.jpg".format('pic',dir, path , path+str(i)), "wb")
            file.write(RawImg.content)
            file.close()
      except Exception:
        pass
    def DownloadImages(self,start=0):
      length = len(self.redirectHTMLs)
      try:
        for i in range(start, length):
            print("Recording {}th out of {}\n{}%\n\n".format(i,length,(i/length *100)))
            redirect = self.redirectHTMLs[i]
            Tags = self.GetImageTagsInImageHTML(redirect[1])
            name = redirect[0]
            if os.path.isdir("pic/{}".format(name)) == False:
                os.mkdir("pic/{}".format(name))
            self.GetImg(Tags, name)
            self.RecordLastSection(str(i))
      except Exception:
        self.DownloadImages(i)
    @staticmethod
    def RecordLastSection(lastsection):
      file = open('lastsection.txt','w')
      file.write(lastsection)
      file.close()
    @staticmethod
    def ReadLastSection():
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
        # self.GetModelsHTML()
        # print("reading model's html done")
        # self.GetRedirectURL()
        # print("Collecting model's picture html files done")
        # self.WriteModels()
        self.ReadModels()
        if os.path.isdir('pic') == False:
            os.mkdir('pic')
        lastRead =self.ReadLastSection()
        if lastRead != None:
          self.DownloadImages(lastRead)
        else:
          self.DownloadImages()

if __name__ == '__main__':
    html = "https://www.elitebabes.com/top-rated-babes/"
    Rylsky = GetRylskyModels(html)
    Rylsky.Run()