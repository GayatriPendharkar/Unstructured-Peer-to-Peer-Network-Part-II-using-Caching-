import socket
import time
import argparse
import sys
import thread
import random
import re
import numpy as np


def NodeServer(Host,Port,max_hops): #Server to keep listening to different messages from other nodes
    sock.bind((Host, Port))
    print 'Socket bind complete'
    while 1:
        request,addr = sock.recvfrom(4096)
        logfile.write(request+' request received at '+time.ctime()+' from '+str(addr)+'\n')
        if request.split(' ')[1]=='JOIN': #to handle JOIN requests
            UpdateRT(request)
            response = '0011 JOINOK 0'
            sock.sendto(response,addr)
            logfile.write(response+' response sent at '+time.ctime()+' to '+str(addr)+'\n')
        elif request.split(' ')[1]=='LEAVE': #to handle LEAVE requests
            response=RemoveIP(request)
            sock.sendto(response,addr)
            logfile.write(response+' response sent at '+time.ctime()+' to '+str(addr)+'\n')
        elif request.split(' ')[1]=='SER': #to search for queries
            searchquery = request.split(' ')[0]+' '+request.split(' ')[1]+' '+request.split(' ')[2]+' '+request.split(' ')[3]+' '+request.split(' ')[5]+' '+re.findall('"([^"]*)"', request)[0]
            if searchquery in search:
                pass
            elif int(request.split(' ')[4])>max_hops:
                pass
            else:
                response=SearchQuery(request)
                search.append(searchquery)
                if response[0].split(' ')[1]=='SER': #to forward to other nodes
                    rep_length = len('SEROK 0')+len(HOST)+len(str(PORT))+len(response[0].split(' ')[4])+len(str(request.split(' ')[5]))+len(re.findall('"([^"]*)"',request)[0])+4
                    rep = str(rep_length).zfill(4)+' SEROK 0 '+HOST+' '+str(PORT)+' '+response[0].split(' ')[4]+' '+str(request.split(' ')[5])+' '+'"'+re.findall('"([^"]*)"',request)[0]+'"'
                    sock.sendto(rep,(request.split(' ')[2],int(request.split(' ')[3])))
                    logfile.write(rep+' file not found and acknowledged at '+time.ctime()+' to '+request.split(' ')[2]+request.split(' ')[3]+'\n')
                    for i in range(len(RoutingTable)):
                        for j in range(len(RoutingTable[RoutingTable.keys()[i]])):
                            sock.sendto(response[0],(RoutingTable.keys()[i],int(RoutingTable[RoutingTable.keys()[i]][j])))
                            logfile.write(response[0]+' search query forwarded at '+time.ctime()+' to '+RoutingTable.keys()[i]+' '+RoutingTable[RoutingTable.keys()[i]][j]+'\n')
                else:
                    for i in range(len(response)): #to reply to the query seeking node
                        sock.sendto(response[i],(request.split(' ')[2],int(request.split(' ')[3])))
                        logfile.write(response[i]+' search response sent at '+time.ctime()+' to '+request.split(' ')[2]+' '+request.split(' ')[3]+'\n')
        elif request.split(' ')[1] == 'SEROK': #to receive search results
            latency.append(abs(time.time()-float(request.split(' ')[6])))
            if request.split(' ')[2] == '1':
                hops.append(int(request.split(' ')[5]))
            logfile.write(request+' search response received at '+time.ctime()+'\n')

        elif request.split(' ')[1] == 'SEARCH': #to receive queries from query generator
            searchreq_len = len('SER')+len(HOST)+len(str(PORT))+len(str(max_hops))+len(str(time.time()))+len(re.findall('"([^"]*)"',request)[0])+4
            searchreq = str(searchreq_len).zfill(4)+' SER '+HOST+' '+str(PORT)+' 00 '+str(time.time())+' '+'"'+str(re.findall('"([^"]*)"',request)[0])+'"'
            search.append(searchreq.split(' ')[0]+' '+searchreq.split(' ')[1]+' '+searchreq.split(' ')[2]+' '+searchreq.split(' ')[3]+' '+searchreq.split(' ')[5]+' '+re.findall('"([^"]*)"', searchreq)[0])
            for i in range(len(RoutingTable)):
                for j in range(len(RoutingTable[RoutingTable.keys()[i]])):
                    sock.sendto(searchreq,(RoutingTable.keys()[i],int(RoutingTable[RoutingTable.keys()[i]][j])))
                    logfile.write(searchreq+' search request sent at '+time.ctime()+' to '+RoutingTable.keys()[i]+str(RoutingTable[RoutingTable.keys()[i]][j]))


def NodeClient(host,Port,msg): #to communicate with bootstrap server and other nodes initially
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(2)
    logfile.write(msg+' request sent at '+time.ctime()+' to '+host+str(Port)+'\n')
    s.sendto(msg,(str(host),int(Port)))
    try:
        reply,server = s.recvfrom(1024)
        logfile.write(reply+' response received at '+time.ctime()+' from '+str(server)+'\n')
    except socket.timeout:
        reply = 'Connection failed, ERROR 9 NODE is busy or non existent'
    s.close()
    return reply

def GenCom(command,IP,Port):
    length = len(command)+len(IP)+len(str(Port))+4
    com = str(length).zfill(4)+' '+command+' '+IP+' '+str(Port)
    return com

def FillRT(reply): #to fill Routing Table with values given by bootsrap server
    for i in range(int(reply.split(' ')[3])):
        if reply.split(' ')[(2*(i+1))+2] in RoutingTable:
            RoutingTable[reply.split(' ')[(2*(i+1))+2]].append(reply.split(' ')[(2*(i+1))+3])
        else:
            RoutingTable[reply.split(' ')[(2*(i+1))+2]]=[reply.split(' ')[(2*(i+1))+3]]
    print(RoutingTable)

def UpdateRT(request): #to update Routing Table as other nodes communicate to JOIN network
    if RoutingTable.has_key(str(request.split(' ')[2])):
        if str(request.split(' ')[3]) not in RoutingTable[request.split(' ')[2]]:
            print 'appending'
            RoutingTable[request.split(' ')[2]].append(request.split(' ')[3])
    else:
        RoutingTable[request.split(' ')[2]]=[request.split(' ')[3]]
        print 'adding'
    print(RoutingTable)

def leaveRT(request): #to notify LEAVE to other nodes in network
    for i in range(len(RoutingTable)):
        for j in range(len(RoutingTable[RoutingTable.keys()[i]])):
            leave_request = NodeClient(RoutingTable.keys()[i],RoutingTable[RoutingTable.keys()[i]][j],request)
            if leave_request.split(' ')[2] == '0':
                print 'Connection terminated successfully with',RoutingTable.keys()[i],RoutingTable[RoutingTable.keys()[i]][j]
            else:
                print 'Connection termination unsuccesul with',RoutingTable.keys()[i],RoutingTable[RoutingTable.keys()[i]][j]

def RemoveIP(req): #to update Routing Table on receiving information about leaving nodes
    if RoutingTable.has_key(req.split(' ')[2]):
        if req.split(' ')[3] in RoutingTable[req.split(' ')[2]]:
            RoutingTable[req.split(' ')[2]].remove(req.split(' ')[3])
            if len(RoutingTable[req.split(' ')[2]]) == 0:
               del RoutingTable[req.split(' ')[2]]
            print RoutingTable
            reply = '0012 LEAVEOK 0'
        else:
            reply = '0015 LEAVEOK 9999'
    else:
        reply = '0015 LEAVEOK 9999'
    return reply

def GenEntry(number,fname): #to generate entries from resources for the node
    f = open('resources.txt','rb')
    res = f.readlines()
    i = 0
    while i<len(res):
        if res[i].startswith('#'):
            res.pop(i)
        else:
            i = i+1
    resources = random.sample(res,number)
    file = open(fname,'wb')
    for j in range(len(resources)):
        file.write(resources[j])

    file.close()
    f.close()

def SearchQuery(search_request): #to search entries for query received
    resource = open(filename,'rb')
    res = resource.read().splitlines()
    query = re.findall('"([^"]*)"', search_request)
    hops = str(int(search_request.split(' ')[4])+1).zfill(2)
    result = [x for x in res if re.search(query[0].lower(), x.lower())]
    search_responses = []
    if len(result)>0:
        for i in range(len(result)):
            lent = len('SEROK 1')+len(HOST)+len(str(PORT))+len(str(hops))+len(str(search_request.split(' ')[5]))+len(result[i])+4
            response = str(lent).zfill(4)+' '+'SEROK 1'+' '+HOST+' '+str(PORT)+' '+str(hops)+' '+str(search_request.split(' ')[5])+' '+'"'+str(result[i])+'"'
            search_responses.append(response)
        return search_responses
    else:
        forward = search_request.split(' ')[0]+' '+search_request.split(' ')[1]+' '+search_request.split(' ')[2]+' '+search_request.split(' ')[3]+' '+hops+' '+search_request.split(' ')[5]+' '+'"'+re.findall('"([^"]*)"', search_request)[0]+'"'
        forward = [forward]
        return forward



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-b','--bootstrap_ip',help = 'Bootstap server IP address',required=True)
    parser.add_argument('-p','--portnumber',help = 'port number of node',required=True)
    parser.add_argument('-n','--bootstrap_port',help= 'Bootstrap port number',required=True)
    parser.add_argument('-a','--action',help= 'REG for register and DEL to delete username or IP address from BS',required=True)
    parser.add_argument('-e','--entry',help='Number of entires for each node from resources(Should be integer only',required=False)
    args = vars(parser.parse_args())
    RoutingTable ={}
    BootStrapIP = args['bootstrap_ip']
    BootStrapPort = abs(int(args['bootstrap_port']))
    HOST = socket.gethostbyname(socket.getfqdn())
    PORT = abs(int(args['portnumber']))
    max_hops = 10
    if len(str(PORT))>5:
        print 'Port number must be at most five digits only'
        sys.exit()
    username = 'ESHWAR'
    action = args['action']
    logfilename = HOST+str(PORT)+'.log'
    logfile = open(logfilename,'wb')
    if action == 'REG': 
        if len(RoutingTable)==0:
            length = len('REG')+len(HOST)+len(str(PORT))+len(username)+4
            msg = str(length).zfill(4)+' '+'REG'+' '+HOST+' '+str(PORT)+' '+username
            print('Attempting to register')
            reply = NodeClient(BootStrapIP,BootStrapPort,msg)
            if int(reply.split(' ')[3])==9999:
                print 'Error in registering, try again'
                sys.exit()
            elif int(reply.split(' ')[3])==9998:
                print 'Already registered, unregister first'
                unregister = raw_input('Do you want to unregister? Y/N: ')
                if unregister == 'Y':
                    length1 = len('DEL')+len('IPADDRESS')+len(HOST)+len(str(PORT))+len(username)+4
                    msg1 = str(length1).zfill(4)+' '+'DEL IPADDRESS'+' '+HOST+' '+str(PORT)+' '+username
                    request = NodeClient(BootStrapIP,BootStrapPort,msg1)
                    print request
                    sys.exit()
                elif unregister=='N':
                    sys.exit()
                else:
                    print 'Invalid input, Please try again later'
                    sys.exit()
            elif 0<=int(reply.split(' ')[3])<=3 :
                FillRT(reply)
        num_entries =abs(int(args['entry']))
        filename = HOST+str(PORT)+'.txt'
        GenEntry(num_entries,filename)
        if len(RoutingTable)>0:
            for i in range(len(RoutingTable)):
                for j in range(len(RoutingTable[RoutingTable.keys()[i]])):
                    join_request = GenCom('JOIN',HOST,PORT)
                    join_response = NodeClient(RoutingTable.keys()[i],int(RoutingTable[RoutingTable.keys()[i]][j]),join_request)
                    print join_response

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        search = []
        hops=[]
        latency = []
        thread.start_new_thread(NodeServer,(HOST,PORT,max_hops))
        leave = ''
        while leave != 'LEAVE': #to take prompts from user while the program is running
            leave = raw_input('INPUT')
            if leave == 'LEAVE':
                leave_length = len('LEAVE')+len(HOST)+len(str(PORT))+4
                leave_msg = str(leave_length).zfill(4)+' '+'LEAVE '+HOST+' '+str(PORT)
                leaveRT(leave_msg)
                length1 = len('DEL')+len('IPADDRESS')+len(HOST)+len(str(PORT))+len(username)+4
                msg1 = str(length1).zfill(4)+' '+'DEL IPADDRESS'+' '+HOST+' '+str(PORT)+' '+username
                request = NodeClient(BootStrapIP,BootStrapPort,msg1)
                print request
                sys.exit()
            elif leave == 'SEARCH':
                fileToSearch=raw_input('Enter word to search: ')
                searchreq_len = len('SER')+len(HOST)+len(str(PORT))+len(str(max_hops))+len(str(time.time()))+len(fileToSearch)+4
                searchreq = str(searchreq_len).zfill(4)+' SER '+HOST+' '+str(PORT)+' 00 '+str(time.time())+' '+'"'+str(fileToSearch)+'"'
                print searchreq
                search.append(searchreq.split(' ')[0]+' '+searchreq.split(' ')[1]+' '+searchreq.split(' ')[2]+' '+searchreq.split(' ')[3]+' '+searchreq.split(' ')[5]+' '+re.findall('"([^"]*)"', searchreq)[0])
                for i in range(len(RoutingTable)):
                    for j in range(len(RoutingTable[RoutingTable.keys()[i]])):
                        sock.sendto(searchreq,(RoutingTable.keys()[i],int(RoutingTable[RoutingTable.keys()[i]][j])))
                        logfile.write(searchreq+' search request sent at '+time.ctime()+' to '+RoutingTable.keys()[i]+str(RoutingTable[RoutingTable.keys()[i]][j]))
            elif leave == 'DEL IPADDRESS':
                length1 = len('DEL')+len('IPADDRESS')+len(HOST)+len(str(PORT))+len(username)+4
                msg1 = str(length1).zfill(4)+' '+'DEL IPADDRESS'+' '+HOST+' '+str(PORT)+' '+username
                request = NodeClient(BootStrapIP,BootStrapPort,msg1)
                print request
                sys.exit()
            elif leave == 'DEL UNAME':
                length1 = len('DEL')+len('UNAME')+len(username)+4
                msg1 = str(length1).zfill(4)+' '+'DEL UNAME'+' '+username
                request = NodeClient(BootStrapIP,BootStrapPort,msg1)
                print request
                sys.exit()
            elif leave == 'LATENCY':
                print latency
                print 'minimum latency:',min(latency)
                print 'maximum latency: ',max(latency)
                print 'standard deviation of latency: ',np.std(latency)
                print 'mean of latency: ',np.mean(latency)
            elif leave == 'HOPS':
                print hops
                print 'minimum hops: ',min(hops)
                print 'maximum hops: ',max(hops)
                print 'standard deviation of hops: ',np.std(hops)
                print 'mean of hops: ',np.mean(hops)
                print 'number of messages processed: ',len(search)
                routing_size = 0
                for i in range(len(RoutingTable)):
                    for j in range(len(RoutingTable[RoutingTable.keys()[i]])):
                        routing_size += 1
                print 'Routing table size: ',routing_size

    elif action == 'DEL':
        delete_action = raw_input('Enter IPADDRESS if you want delete current IP or enter UNAME to delete current username')
        if delete_action == 'IPADDRESS':
            length1 = len('DEL')+len('IPADDRESS')+len(HOST)+len(str(PORT))+len(username)+4
            msg1 = str(length1).zfill(4)+' '+'DEL IPADDRESS'+' '+HOST+' '+str(PORT)+' '+username
            request = NodeClient(BootStrapIP,BootStrapPort,msg1)
            print request
            sys.exit()
        elif delete_action == 'UNAME':
            length1 = len('DEL')+len('UNAME')+len(username)+4
            msg1 = str(length1).zfill(4)+' '+'DEL UNAME'+' '+username
            request = NodeClient(BootStrapIP,BootStrapPort,msg1)
            print request
            sys.exit()
        else:
            print 'Invalid input, Please try again later'
            sys.exit()
    else:
        print 'Invalid input, Please try again later'
        sys.exit()
