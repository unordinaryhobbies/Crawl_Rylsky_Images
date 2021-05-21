from os import altsep
from bs4 import BeautifulSoup
import requests
from requests.api import request
import os

class GetRylsky():
    def __init__(self, html):
        self.GetMainHtml = requests.get(html)
        self.mainHTML = BeautifulSoup(self.GetMainHtml.content, 'lxml')
        self.redirects = []
    def GetImageTagsInImageHTML(self, redirectHTML):
        imageLink = []
        ul = redirectHTML.find('ul', class_='list-gallery a css')
        try:
            imageTags = ul.find_all('img')
        except Exception:
            return
        for tag in imageTags:
            imageLink.append(tag)
        return imageLink

    def GetImg(self, ImgLinks):
        for i in range(len(ImgLinks)):
            img = ImgLinks[i]
            path = img['alt'].replace(' ','_')
            RawImg = requests.get(img['src'])
            if os.path.isdir(path) is False:
                os.mkdir(path)
            print("downloading {}: {}th image".format(path, i))
            file = open("{0}/{1}.jpg".format(path , path+str(i)), "wb")
            file.write(RawImg.content)
            file.close()
    def GetRedirectHTMLs(self):
        ul = self.mainHTML.find('ul', class_= 'gallery-a')
        Links = ul.find_all('a')
        for link in Links:
            redirect = requests.get(link['href'])
            self.redirects.append(BeautifulSoup(redirect.content,'lxml'))
        # print("{}\n".format(self.redirects))
    
    def Run(self):
        self.GetRedirectHTMLs()
        print("Getting redirect web info done...")
        for redirect in self.redirects:
            ImgTags = self.GetImageTagsInImageHTML(redirect)
            if ImgTags is None:
                break;
            else:
                # t = Thread(target = self.GetImg, args=(ImgTags))
                # t.start()
                self.GetImg(ImgTags)

if __name__ == '__main__':
    html = "https://www.elitebabes.com/"
    Rylsky = GetRylsky(html)
    Rylsky.Run()