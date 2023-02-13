import socket
import ipaddress
import psutil
from ctypes import c_uint32 as unsigned_byte


def get_host_ip():
    # IPs = socket.gethostbyname_ex(socket.gethostname())[-1]
    # print(IPs)
    # ip = [a for a in os.popen('route print').readlines()
    #       if ' 0.0.0.0 ' in a][0].split()[-2]
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


def get_boardcast_ip():
    local_ip = ipaddress.ip_address(get_host_ip())
    netmask = ipaddress.ip_address(0)
    for interface, data in psutil.net_if_addrs().items():
        if (int(netmask)):
            break
        for addr in data:
            # if not addr.netmask:
            #     continue
            # print('address  :', addr.address)
            # print('netmask  :', addr.netmask)
            try:
                address = ipaddress.ip_address(addr.address)
                if int(local_ip) == int(address):
                    netmask = ipaddress.ip_address(addr.netmask)
                    break
            except:
                ...
    # print(local_ip, address, netmask)
    # print(unsigned_byte(~int(netmask)).value)
    boardcast_ip = ipaddress.ip_address(
        int(address) | unsigned_byte(~int(netmask)).value)
    return str(boardcast_ip)
