# Unstructured-Peer-to-Peer-Network-Part-II-using-Caching-

open unstructured_caching.py on a unix terminal as shown below:
$python unstructured_caching.py -p <port_num> -b <bootstrap_ip> -n <bootstrap_port> -e <num_of_entries> -a<action> -s<size_of_cache>

1. port_num is the argument for binding the node to a particular port
2. num_of_entries is to decide the number of entries each node should choose from the resources.txt
3. action is to specify if you want the node to be registered or deleted. Enter REG to register at the bootstrap or DEL to delete at the bootstrap server
4. upon choosing DEL, the program asks for a prompt to choose between deleting IPADDRESS and username. type IPADDRESS for unregistering IP and port or type UNAME for unregistering all the ports under that username
5. If you choose REG for action, the program starts communicating with the addresses provided by the bootstrap server and once the connections are established, it starts listening for incoming messages.
6. You type in LEAVE, DEL IPADDRESS, DEL UNAME or SEARCH in the prompt while the program is running to perform those actions
7. If you type SEARCH, it will prompt for the word to search.
8. The word to search is case insensitive unlike the above prompts and returns all the file names matching the requested key word.
9. Once required number of nodes are opened you can use query.py to generate queries.

open query.py and it prompts for an 's' value to generate a zipf distribution

10. Once the value is given as standard input, this query.py communicates with the nodes in the network and passes queries to search for in the network.
11. Once all the queries generated are sent to the network one by one, query.py will exit
12. You can now type LATENCY to get results related to latency of that node in the node terminal
13. If you type HOPS in the node terminal, it will print results related to hops of that node

Note: except for the search prompt all other standard prompts are case sensitive and must be typed in uppercase letters only
