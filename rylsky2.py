from bs4 import BeautifulSoup
import requests
import os
from time import sleep

class GetRylskyModels():
    def __init__(self, html):
        self.GetMainHtml = requests.get(html)
        self.mainHTML = BeautifulSoup(self.GetMainHtml.content, 'lxml')
        self.modelHTMLs = []
        self.redirectHTMLs = []
        self.modelName = []
    def GetModelsHTML(self):
        ULs = self.mainHTML.find_all('ul',class_='gallery-a a d')

        for ul in ULs:
            As = ul.find_all('a')
            print("-------------------------------------------------------------")
            for a in As:
                name = a.find_all('span')[-1].text
                print(name)
                self.modelName.append(name)
                # print("{}\n\n".format(a['href']))
                self.modelHTMLs.append(a['href'])

    def GetRedirectURL(self):
        i = 0
        for HTML in self.modelHTMLs:
            print("Reading {}th model's website".format(i))
            html = requests.get(HTML)
            HTML = BeautifulSoup(html.content, 'lxml')
            ULs = HTML.find_all('ul', class_ = 'gallery-a b')
            i += 1
            sleep(2)
            for ul in ULs:
                As = ul.find_all('a')
                for a in As:
                    # print("{}\n\n".format(a['href']))
                    self.redirectHTMLs.append(a['href'])

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