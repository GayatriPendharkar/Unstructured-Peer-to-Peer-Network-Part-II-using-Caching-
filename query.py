import socket
import numpy as np
import random
import time

def NodeClient(host,Port,msg): #to communicate with bootstrap server
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(2)
    s.sendto(msg,(str(host),int(Port)))
    try:
        reply,server = s.recvfrom(1024)
    except socket.timeout:
        reply = 'Connection failed, ERROR 9 NODE 10000 is busy or non existent'
    s.close()
    return reply

def zipf(s,N): #to generate zipf's distribution
    temp = np.power(np.arange(1,N+1),-s)
    zeta = np.r_[0.0,np.cumsum(temp)]
    distMap = [x/zeta[-1] for x in zeta]
    u = np.random.random(N)
    v = np.searchsorted(distMap,u)
    samples = [t-1 for t in v]
    return samples

if __name__ == '__main__':
    BootStrapIP = '129.82.46.226'
    BootStrapPort = 10000
    username = 'ESHWAR'
    len_msg = len('GET IPLIST')+len(username)+4
    msg = str(len_msg).zfill(4)+' GET IPLIST '+username
    reply = NodeClient(BootStrapIP,BootStrapPort,msg)
    print reply
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    nodes = []
    if int(reply.split(' ')[5])<9999:
        for i in range(int(reply.split(' ')[5])):
            nodes.append(reply.split(' ')[2*(i+1)+4]+' '+reply.split(' ')[2*(i+1)+5])
    q_file = open('resources.txt','rb')
    queries = q_file.read().splitlines()
    j=0
    while j<len(queries):
        if queries[j].startswith('#'):
            queries.pop(j)
        else:
            j+=1
    s = raw_input('Enter value for s as float only: ')
    q_index = zipf(float(s),160)
    for i in range(len(q_index)): #to select query and sending to any 5 random nodes
        query = queries[q_index[i]]
        search_nodes = random.sample(nodes,5)
        for i in range(len(search_nodes)):
            q_len = len(query)+len('SEARCH')+4
            q = str(q_len).zfill(4)+' SEARCH '+' '+'"'+query+'"'
            print q
            sock.sendto(q,(search_nodes[i].split(' ')[0],int(search_nodes[i].split(' ')[1])))
        time.sleep(1)

