from bs4 import BeautifulSoup
import requests
import os
import time
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
                self.redirects = read.read()
    def WriteModels(self):
        with open(self.modelFile,'a') as Write:
            for redirect in self.redirectHTMLs:
                Write.write("{},{}\n".format(redirect[0], redirect[1]))
    def GetRedirectURL(self):
        i = 0
        info = []
        for modelHTML in self.modelHTMLs:
            print("{}, {}\n".format(modelHTML[0], modelHTML[1]))
            # print("Reading {}th model's website".format(i))
            html = requests.get(modelHTML[1])
            HTML = BeautifulSoup(html.content, 'lxml')
            ULs = HTML.find_all('ul', class_ = 'gallery-a b')
            for ul in ULs:
                As = ul.find_all('a')
                for a in As:
                    info.append(modelHTML[0])
                    info.append(a['href'])
                    # print("{}\n\n".format(info))
                    self.redirectHTMLs.append(info)
                    info.clear()

    def GetImageTagsInImageHTML(self, redirectHTML):
        imageLink = []
        html = requests.get(redirectHTML)
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
        for i in range(len(ImgLinks)):
            img = ImgLinks[i]
            path = img['alt'].replace(' ','_')
            RawImg = requests.get(img['src'])
            if os.path.isdir("{0}/{1}".format(dir,path)) == False:
                os.mkdir("{0}/{1}".format(dir,path))
            print("downloading {}: {}th image".format(path, i))
            file = open("{0}/{1}/{2}.jpg".format(dir, path , path+str(i)), "wb")
            file.write(RawImg.content)
            file.close()
    def Run(self):
        self.GetModelsHTML()
        print("reading model's html done")
        self.GetRedirectURL()
        print("Collecting model's picture html files done")
        self.WriteModels()
        i = 0
        # for redirect in self.redirectHTMLs:
        #     Tags = self.GetImageTagsInImageHTML(redirect)
            # name = self.modelName[i]
            # if os.path.isdir(name) == False:
            #     os.mkdir(name)
            # self.GetImg(Tags, name)
            # i += 1


if __name__ == '__main__':
    html = "https://www.elitebabes.com/top-rated-babes/"
    Rylsky = GetRylskyModels(html)
    Rylsky.Run()
    time.sleep(300)