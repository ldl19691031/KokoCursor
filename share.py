import rpyc
import configparser

def get_connection():
    config = configparser.ConfigParser()
    config.read('config.ini')
    ip_address = config.get('Network', 'ip_address')
    port = config.get('Network', 'port')
    conn = rpyc.connect(ip_address, port)
    return conn