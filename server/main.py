import socket
import json
from util import get_boardcast_ip,get_host_ip

# LISTEN_PORT = 23333
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

devices_ip=[('192.168.1.184',33333)]

def find_device(port,_socket):
    host_ip=get_host_ip()
    boardcast_ip=get_boardcast_ip()
    print("send to "+boardcast_ip +' for discovery.')
    data=json.dumps({'cmd':'discover','port':int(port),'server_ip':host_ip})
    print('send'+data)
    _socket.sendto(data.encode('utf-8'), (boardcast_ip, int(port)))


def play(device,url,fmt=None):
    data=json.dumps({'cmd':'play','url':url,'fmt':fmt})
    print('send'+data +'to '+device[0]+':'+str(device[1]))
    s.sendto(data.encode('utf-8'), (device[0], int(device[1])))

# s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)


# s.bind(('', PORT))
# print('Listening for broadcast at ', s.getsockname())

# while True:
#     data, address = s.recvfrom(65535)
#     print('Server received from {}:{}'.format(address, data.decode('utf-8')))

play(devices_ip[0],'http://meting-ve.2333332.xyz/api?server=netease&type=url&id=473403185')
