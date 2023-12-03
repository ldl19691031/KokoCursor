import rpyc
import win32gui,win32ui
import win32api
from win32api import GetSystemMetrics
import win32api
import win32con
from share import get_connection
conn = get_connection()

slave_key = input("Enter the slave key: ")
slave = conn.root.query_slave(slave_key)
if slave is None:
    print("Invalid slave key.")
    exit(1)
else:
    print("Start control slave : " + str(slave_key))
    print("Press Alt to start control.")
    
last_x, last_y = win32api.GetCursorPos()

try:
    while True:    
        x, y = win32api.GetCursorPos()
        if x != last_x or y != last_y:
            dx = x - last_x
            dy = y - last_y
            if win32api.GetAsyncKeyState(win32con.VK_MENU) < 0:
                conn.root.move_slave(slave_key, dx, dy)
            last_x = x
            last_y = y
except KeyboardInterrupt:
    conn.close()
    print("Control stopped.")
    exit(0)
except Exception as e:
    conn.close()
    print("Error: " + str(e))
    exit(0)
