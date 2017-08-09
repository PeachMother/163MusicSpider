import db
from Crypto.Cipher import AES
import base64
import requests
import pymysql
import common


class Comment(object):
    """docstring for Comment"""
    def __init__(self, configFile = '163Spider.conf'):
        self.__db = db.MySQLDB()
        if configFile != '163Spider.conf':
            self.__db.setConfig(configFile)
        self.__headers = {
        'Host':'music.163.com',
        'Referer':'http://music.163.com/',
        'User-Agent':'Mozilla/5.0 (PlayBook; U; RIM Tablet OS 2.1.0; en-US) AppleWebKit/536.2+ (KHTML like Gecko) Version/7.2.1.0 Safari/536.2+',
        'Accept':'*/*'
        }
        self.__baseUrl = "http://music.163.com/weapi/v1/resource/comments/R_SO_4_%s/?csrf_token="
        self.__encSecKey = '257348aecb5e556c066de214e531faadd1c55d814f9be95fd06d6bff9f4c7a41f831f6394d5a3fd2e3881736d94a02ca919d952872e7d0a50ebfa1769a7a62d512f5f1ca21aec60bc3819a9c3ffca5eca9a0dba6d6f7249b06f5965ecfff3695b54e1c28f3f624750ed39e7de08fc8493242e26dbc4484a01c76f739e135637c'

    
    def isSingle(self,song_id):
        sql = 'select `song_id` from `music` where `song_id` = "%s"' %(song_id)
        results = self.__db.querySQL(sql)
        if len(results) > 0:
            return False
        else:
            return True


    def isSingleList(self,href):
        sql = 'select `id` from `playlist163` where `link` = "%s"' %(str(href))
        results = self.__db.querySQL(sql)
        if len(results) > 0:
            return False
        else:
            return True    




    def getSongIds(self,maxval = 100):
        sql = 'select `song_id` from `music163` where over = "N" limit %s' %(str(maxval))
        results = self.__db.querySQL(sql)
        return results


    def aesEncrypt(self,source,key,iv):
        blockSize = AES.block_size
        pad = lambda s : s + (blockSize - len(s) % blockSize) * chr(blockSize - len(s) % blockSize).encode()

        encryptor = AES.new(key,AES.MODE_CBC,iv)

        sourceByte = source.encode()
        encryptText = encryptor.encrypt(pad(sourceByte))

        return base64.b64encode(encryptText)

    def createParams(self,page = 1):
        if page == 1:
            text = '{"rid":"","offset":"0","total":"true","limit":"20","csrf_token":""}'
        else:
            offset = str((page - 1) * 20)
            text = '{"rid":"","offset":"%s","total":"%s","limit":"20","csrf_token":""}' %(offset,'false')

        firstKey = '0CoJUm6Qyw8W8jud'
        secondKey = 'FFFFFFFFFFFFFFFF'
        iv = '0102030405060708'

        encText = self.aesEncrypt(self.aesEncrypt(text,firstKey,iv).decode(),secondKey,iv)
        return encText.decode()

    def viewCapture(self,song_id,page = 1):
        if page == 1:
            sql = 'delete from `comment163` where `song_id` = "%s"' %(song_id)
            self.__db.insertSQL(sql)

        url = self.__baseUrl %(song_id)
        data = {
        'params':self.createParams(page),
        'encSecKey':self.__encSecKey
        }


        response = requests.post(url,headers = self.__headers,data = data,timeout = 10)


        try:
            responseJson = response.json()
            for comment in responseJson['comments']:
                if comment['likedCount'] > 30:
                    song_id = str(song_id)
                    text = pymysql.escape_string(comment['content'])
                    author = pymysql.escape_string(comment['user']['nickname'])
                    liked = comment['likedCount']

                    sql = 'insert into `comment163` (`song_id`,`text`,`author`,`liked`) values ("%s","%s","%s","%s")' %(song_id,text,author,liked)
                    self.__db.insertSQL(sql)
            if page == 1:
                for comment in responseJson['hotComments']:
                    song_id = str(song_id)
                    text = pymysql.escape_string(comment['content'])
                    author = pymysql.escape_string(comment['user']['nickname'])
                    liked = comment['likedCount']
                    sql = 'insert into `comment163` (`song_id`,`txt`,`author`,`liked`) values ("%s","%s","%s","%s")' %(song_id,text,author,liked)
                    self.__db.insertSQL(sql)

            updateSql = 'update `music163` set `over` = "Y", `comment` = "%s" where `song_id` = "%s"' %(str(responseJson['total']),str(song_id))
            self.__db.insertSQL(sql)
            return responseJson['total']/20

        except KeyboardInterrupt as e:
            print('INFO:解释器请求退出')
            common.Log("ERROR 107 : 解释器请求退出")
            exit()
        except Exception as e:
            common.Log('ERROR 910:SONG_ID-%s,PAGE-%s' %(str(song_id),str(page)))
            self.viewsCapture(song_id,page,page+1)


    def viewLinks(self,song_id):
        pass


    def viewsCapture(self,song_id,page = 1,pages = 1024):
        if page > 1:
            while page < pages:
                pages = self.viewCapture(song_id,page)
                page = page + 1
        else:
            self.viewCapture(song_id,1)
        self.viewLinks(song_id)





















if __name__ == '__main__':
    tmp = Comment()
    #results = tmp.getSongIds(maxval = 10)
    results = tmp.viewsCapture('493551017',1,2)
    print(results)
        