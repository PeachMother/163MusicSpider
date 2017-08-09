from configparser import ConfigParser
import pymysql
import common as c

class MySQLDB(object):
    """docstring for ClassName"""
    __db = None
    __cursor = None
    def __init__(self, configFile = '163Spider.conf'):
        config = ConfigParser()
        config.read(configFile)
        host = config.get('mysql','host')
        username = config.get('mysql','username')
        password = config.get('mysql','password')
        database = config.get('mysql','database')

        self.__db = pymysql.connect(host,username,password,database,charset='utf8mb4')
        self.__cursor = self.__db.cursor()
        self.__configFile = configFile

    def setConfig(self,configFile):
        config = ConfigParser()
        config.read(configFile)
        host = config.get('mysql','host')
        username = config.get('mysql','username')
        password = config.get('mysql','password')
        database = config.get('mysql','database')

        self.__db = pymysql.connect(host,username,password,database,charset='utf8mb4')
        self.__cursor = self.__db.cursor()
        self.__configFile = configFile

    def displayConfig(self):
        print('ConfigName:',str(self.__configFile))
        config = ConfigParser()
        config.read(self.__configFile)
        print('Host: ',config.get('mysql','host'))
        print('User: ',config.get('mysql','username'))
        print('Password: ',config.get('mysql','password'))
        print('DataBase: ',config.get('mysql','database'))

    def createTables(self):
        dropSqls = ["drop table if exists playlist163","drop table if exists music163","drop table if exists comment163"]
        for dropSql in dropSqls:
            self.__cursor.execute(dropSql)
        self.__db.commit()

        playlist = """CREATE TABLE `playlist163` (
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `title` varchar(150) DEFAULT '',
        `link` varchar(120) DEFAULT '',
        `cnt` varchar(20) DEFAULT '0',
        `dsc` varchar(50) DEFAULT 'all',
        `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
        `over` varchar(20) DEFAULT 'N',
        PRIMARY KEY(`id`),
        KEY `over_link` (`over`,`link`)) 
        ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4
        """
        music = """CREATE TABLE `music163` (
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `song_id` int(11) DEFAULT NULL,
        `song_name` varchar(200) DEFAULT '',
        `author` varchar(350) DEFAULT '',
        `over` varchar(5) DEFAULT 'N',
        `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
        `comment` int(11) DEFAULT '0',
        PRIMARY KEY(`id`),
        KEY `over_id`(`over`,`id`),
        KEY `author`(`author`),
        KEY `song_id_comment` (`song_id`,`comment`))
        ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4
        """

        comment = """CREATE TABLE `comment163` (
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `song_id` int(11) DEFAULT NULL,
        `txt` mediumtext,
        `author` varchar(100) DEFAULT '注销',
        `liked` int(11) DEFAULT '0',
        PRIMARY KEY(`id`),
        KEY `liked_song_id` (`liked`,`song_id`),
        KEY `song_id_liked` (`song_id`,`liked`))
        ENGINE=InnoDB AUTO_INCREMENT=1418975 DEFAULT CHARSET=utf8mb4
        """

        self.__cursor.execute(playlist)
        self.__cursor.execute(music)
        self.__cursor.execute(comment)
        self.__db.commit()
        print('TABLES RECREATE SUCCESS')

    def querySQL(self,sql):
        self.__cursor.execute(sql)
        results = self.__cursor.fetchall()
        return results

    def insertSQL(self,sql):
        try:
            self.__cursor.execute(sql)
            self.__db.commit()
        except:
            self.__db.rollback()
            c.Log('ERROR 909 : SQL' + sql)

    


        
if __name__ == "__main__":
     tmp = MySQLDB()
     tmp.createTables()