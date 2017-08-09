import logging

def Log(msg):
    logging.basicConfig(filename = 'spider163.log',level = logging.INFO)
    logging.info(msg)