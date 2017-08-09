
import db
import requests
from bs4 import BeautifulSoup
import common
from html.parser import HTMLParser


class Playlist(object):
    """docstring for ClassName"""

    __play_url = None
    __headers = None
    __db = None

    def __init__(self, configFile = "163Spider.conf"):
        self.__headers = {
        'Host':'music.163.com',
        'Referer':'http://music.163.com/',
        'User-Agent':'Mozilla/5.0 (PlayBook; U; RIM Tablet OS 2.1.0; en-US) AppleWebKit/536.2+ (KHTML like Gecko) Version/7.2.1.0 Safari/536.2+',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }

        self.__play_url = 'http://music.163.com/discover/playlist/?order=hot&cat=全部&limit=35&offset='

        self.__db = db.MySQLDB()
        if configFile != '163Spider.conf':
            self.__db.setConfig(configFile)

    def isSinglePlaylist(self,link):
        sql = 'select * from `playlist163` where `link` =  "%s" ' %(link)
        results = self.__db.querySQL(sql)
        if len(results) > 0:
            return False
        else:
            return True


    def viewCapture(self,page):
        play_url = self.__play_url + str((page-1) * 35)
        response = requests.get(play_url,headers = self.__headers)
        soup = BeautifulSoup(response.content,'html.parser')
        ulTag = soup.find('ul',{'class':'m-cvrlst f-cb'})
        for play in ulTag.find_all('div',{'class':'u-cover u-cover-1'}):
            title = play.find('a',{'class':'msk'})['title']
            link = play.find('a',{'class':'msk'})['href']
            cnt = play.find('span',{'class':'nb'}).string
            
            sql = 'insert into `playlist163` (`title`,`link`,`cnt`) values ("%s","%s","%s")' %(title,link,cnt)
            if self.isSinglePlaylist(link) == True:
                self.__db.insertSQL(sql)

            




if __name__ == '__main__':
    tmp = Playlist()
    tmp.viewCapture(1)



    

