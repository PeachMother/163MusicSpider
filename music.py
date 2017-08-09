import db
import requests
from bs4 import BeautifulSoup
import json
import common
import pymysql



class Music(object):
    """docstring for Music"""
    __db = None
    __url = None

    def __init__(self, configFile = '163Spider.conf'):
        self.__headers = {
        'Host':'music.163.com',
        'Referer':'http://music.163.com/',
        'User-Agent':'Mozilla/5.0 (PlayBook; U; RIM Tablet OS 2.1.0; en-US) AppleWebKit/536.2+ (KHTML like Gecko) Version/7.2.1.0 Safari/536.2+',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }
        self.__url = 'http://music.163.com'
        self.__db = db.MySQLDB()
        if configFile != '163Spider.conf':
            self.__db.setConfig(configFile)


    def isSingle(self,song_id):
        sql = ' select `song_id` from music163 where `song_id` = "%s"' %(song_id)
        results = self.__db.querySQL(sql)
        if len(results) > 0:
            return False
        else:
            return True

    def viewCapture(self,link):
        sql = 'update `playlist163` set `over` = "N" where `link` = "%s"'  %(link)
        self.__db.insertSQL(sql)

        url = self.__url + str(link)
        

        response = requests.get(url,headers = self.__headers)
        soup = BeautifulSoup(response.content,'html.parser')
        musics = json.loads(soup.find('textarea',{'style':'display:none;'}).get_text())
        for music in musics:

            name = pymysql.escape_string(music['name'])           
            author = pymysql.escape_string(music['artists'][0]['name'])
            song_id = pymysql.escape_string(str(music['id']))


            sql = 'insert into `music163`(`song_id`,`song_name`,`author`) values ("%s","%s","%s")' %(song_id,name,author)

            if(self.isSingle(song_id)) == True:
                self.__db.insertSQL(sql)
            else:
                common.Log('{} : {},{}'.format("Error 901",url,song_id))


    def viewCaptures(self):
        sql = 'select `link` from `playlist163` where `over` = "N" limit 10'
        urls = self.__db.querySQL(sql)
        
        for url in urls:
            self.viewCapture(url[0])
            #print(url[0])
        for url in urls:
            self.__db.insertSQL('update `playlist163` set `over` = "Y" where `link` = "%s" ' %(str(url[0]))) 

    def getPlaylistRange(self):
        results = self.__db.querySQL('select count(*) from `playlist163` where `over` = "N"')
        #print(results[0][0])
        return results[0][0]



if __name__ == '__main__':
    tmp = Music()
    #tmp.viewCapture('/playlist?id=739396417')
    tmp.viewCaptures()
    tmp.getPlaylistRange()


