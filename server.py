
import random
import rpyc
from rpyc.utils.server import ThreadedServer
from rpyc.utils.helpers import classpartial
import configparser

class MyService(rpyc.Service):
    def __init__(self, sharing_data):
        self.sharing_data = sharing_data

    def exposed_add_slave(self, on_init):
        slave = Slave()
        key = self.sharing_data.add_slave(slave)
        on_init(key)
        print("Slave added successfully, current slave num is " + str(len(self.sharing_data.slaves)))
    
    def exposed_remove_slave(self, key):
        self.sharing_data.remove_slave(key)
        print("Slave removed successfully, current slave num is " + str(len(self.sharing_data.slaves)))
    
    def exposed_query_slave(self, key):
        slave = self.sharing_data.query_slave(key)
        if slave is None:
            return None
        return slave

    def exposed_move_slave(self, key, dx, dy):
        slave = self.sharing_data.query_slave(key)
        if slave is None:
            return
        slave.move(dx, dy)
   
    def exposed_consume_move_slave(self, key):
        slave = self.sharing_data.query_slave(key)
        if slave is None:
            return None
        return slave.consume()
    
class Slave:
    def __init__(self):
        self.dx = 0
        self.dy = 0
    def move(self, x, y):
        self.dx += x
        self.dy += y
    def consume(self):
        dx = self.dx
        dy = self.dy
        self.dx = 0
        self.dy = 0
        return [dx, dy]

class SharingData:
    def __init__(self):
        self.slaves = {}

    def add_slave(self, slave):
        key = self.generate_key()
        while key in self.slaves:
            key = self.generate_key()
        self.slaves[key] = slave
        return key

    def remove_slave(self, key):
        if key in self.slaves:
            del self.slaves[key]

    def query_slave(self, key):
        if key in self.slaves:
            return self.slaves[key]
        return None

    def generate_key(self):
        return str(random.randint(1, 100000))



if __name__ == "__main__":
    sharing_data = SharingData()  # Create a SharingData instance
    service = classpartial(MyService, sharing_data)  # Pass sharing_data as an argument
    config = configparser.ConfigParser()
    config.read('config.ini')
    port = config.get('Network', 'port')
    server = ThreadedServer(service, port=port)
    print("Server started.")
    server.start()
