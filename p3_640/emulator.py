"""Name: Changjae HanDate: Dec 11 2023Email: chan82@wisc.educslogin: changjaeFile: emulator.py"""import socketimport structimport argparseimport timeimport heapq"""readtopology()    1. read topology.txt file    2. save and initial build forward table"""def readtopology(this_ip_port, filename, emulator_port):        graph = {}    with open(filename, 'r') as file:        line = file.readline()        while line:            #get info about node and neighbors            node_info = line.strip().split(' ')            node = node_info[0]            neighbors_info = node_info[1:]            #changes it to set            neighbors = {(neighbor.split(',')[0], int(neighbor.split(',')[1])) for neighbor in neighbors_info}            #add info to graph            graph[(node.split(',')[0], int(node.split(',')[1]))] = neighbors            line = file.readline()    emulator_ip, emulator_port = this_ip_port    start_node = (emulator_ip, emulator_port) #cur node        return graph, buildForwardTable(graph, start_node)"""sendHello()    1. send Hello message to all neighbors at defined interval"""def sendHello(emulator_socket, route_topology, cur_ip_port, neighborTimestamp):        cur_ip, cur_port = cur_ip_port        #Find neighbors    for ip_port in route_topology[cur_ip_port]:        neighbor_ip, neighbor_port = ip_port        header = struct.pack("!cI4sH4sH", b'H', 0, socket.inet_aton(cur_ip), cur_port, socket.inet_aton(neighbor_ip), neighbor_port)        payload = "Hello"        packet = header + payload.encode()        emulator_socket.sendto(packet, (neighbor_ip, neighbor_port))   """generate_sendLink()    a) The (ip, port) pair of the node that created the message.    b) A list of directly connected neighbors of that node, with the cost of the link to each one.    c) A sequence number.     d) A time to live (TTL) for this packet.     generate new link state packet and send to neighbors at defined interval or whenever info is updated"""        def generate_sendLink(emulator_socket, route_topology, cur_ip_port, seq_no):        cur_ip, cur_port = cur_ip_port        TTL = 3    neighbor_list = [(ip, port, 1) for ip, port in list(route_topology[cur_ip_port])] #create neighbor info list        #Find neighbors    for ip_port in route_topology[cur_ip_port]:        neighbor_ip, neighbor_port = ip_port        header = struct.pack('!c4sHII', b'L', socket.inet_aton(cur_ip),cur_port, seq_no, TTL)        packet = header + b''.join(struct.pack('4sHI', socket.inet_aton(ip), port, cost) for (ip, port, cost) in neighbor_list)          emulator_socket.sendto(packet, (neighbor_ip, neighbor_port))        """updateTopology()    1. If True, node is newly added (back to alive)    2. If False, node is removed    apply to the topology file"""def updateTopology(route_topology, cur_ip_port, source_ip, source_port, update, status):        if status:        route_topology[cur_ip_port].add((source_ip, source_port))    else:        for node in update:            route_topology[cur_ip_port].remove(node)        update = []            return update"""forwardpacket()    1. For link state packet, do reliable flooding (send LSP to all neighbors except the node pkt received)    2. For route trace packet, utilizing forward table to send the packet with the shortest paths"""def forwardpacket(emulator_socket, route_topology, forward_table, cur_ip_port, received_packet, neighborSequence, ptype):        cur_ip, cur_port = cur_ip_port        #If it is LSP    if ptype == 'L':        header = received_packet[:15]        neighbor_data = received_packet[15:]                _, source_ip, source_port, seq_no, TTL = struct.unpack('!c4sHII',header)                if TTL:            TTL = TTL - 1 #Decrement TTL                        #First Time to get LSP for this node, save and do flooding             if not (socket.inet_ntoa(source_ip), source_port) in neighborSequence:                neighborSequence[(socket.inet_ntoa(source_ip), source_port)] = seq_no                #Find neighbors                for (neighbor_ip, neighbor_port) in route_topology[cur_ip_port]:                    if neighbor_ip == socket.inet_ntoa(source_ip) and neighbor_port == source_port:                        pass #Don't send to the node where LSP comes from                    else: #Flooding to neighbor                        header = struct.pack('!c4sHII', b'L', socket.inet_aton(cur_ip),cur_port, seq_no, TTL)                        packet = header + neighbor_data                          emulator_socket.sendto(packet, (neighbor_ip, neighbor_port))                                    else: #If not the first time, compare seq_no and flooding only when new sequence number is greater than old one                if seq_no > neighborSequence[(socket.inet_ntoa(source_ip), source_port)]:                    neighborSequence[(socket.inet_ntoa(source_ip), source_port)] = seq_no                    for (neighbor_ip, neighbor_port) in route_topology[cur_ip_port]:                        if neighbor_ip == socket.inet_ntoa(source_ip) and neighbor_port == source_port:                            pass #Same                        else:                            header = struct.pack('!c4sHII', b'L', socket.inet_aton(cur_ip),cur_port, seq_no, TTL)                            packet = header + neighbor_data                            emulator_socket.sendto(packet, (neighbor_ip, neighbor_port))                   else: #If new sequence number is smaller, it is old one, ignore                    pass        else: #TTL is 0, so delete (ignore)            pass     #If it is route trace packet    if ptype == 'T':        header = received_packet[:17]        payload = received_packet[17:].decode()        packet_type, trace_TTL, source_ip, source_port, dest_ip, dest_port = struct.unpack("!cI4sH4sH",header)                 if trace_TTL:            trace_TTL = trace_TTL - 1 #Decrement TTL            #Find nexthop addr and port            key_for_next = (socket.inet_ntoa(dest_ip), dest_port)                nexthop_addr = forward_table[key_for_next]['next_hop'][0]            nexthop_port = forward_table[key_for_next]['next_hop'][1]             #Send pkt to the next hop            header = struct.pack("!cI4sH4sH", packet_type, trace_TTL, source_ip, source_port, dest_ip, dest_port)            payload = payload + cur_ip + "," + str(cur_port) + ","            packet = header + payload.encode()            emulator_socket.sendto(packet, (nexthop_addr, nexthop_port))        else: #TTL=0, create new route trace packet and send back to route tracer            new_header = struct.pack("!cI4sH4sH", packet_type, trace_TTL, socket.inet_aton(cur_ip), cur_port, dest_ip, dest_port)             payload = payload + cur_ip + "," + str(cur_port)            new_packet = new_header + payload.encode()            emulator_socket.sendto(new_packet, (socket.inet_ntoa(source_ip), source_port))    """createroutes()    a) The route topology     b) The forwarding table     c) The latest timestamp (neighbor)    d) The largest sequence number (neighbor) of the received LinkStateMessages from each node except itself"""def createroutes(emulator_socket, cur_ip_port, route_topology, forward_table):            update = [] #use when needed update        neighborTimestamp = {} #save timestamp to manage hellomessage at defined interval    neighborSequence = {} #save largest sequence number to keep updated    sent_seq_no = 0        for ip_port in route_topology[cur_ip_port]:        neighbor_ip, neighbor_port = ip_port        neighborTimestamp[(neighbor_ip,neighbor_port)] = time.time()        startCond = True    helloInterval = time.time()    linkInterval = time.time()    cur_ip, cur_port = cur_ip_port        while True:                #At defined interval, send Hello message to neighbors        if time.time()-helloInterval > 1 or startCond:            sendHello(emulator_socket, route_topology, cur_ip_port, neighborTimestamp)            helloInterval = time.time()                #At defined interval, generate and send LSP to neighbors        if time.time()-linkInterval > 1 or startCond:            generate_sendLink(emulator_socket, route_topology, cur_ip_port, sent_seq_no)            sent_seq_no = sent_seq_no + 1            linkInterval = time.time()                startCond = False                try:            received_packet,(ip,port) = emulator_socket.recvfrom(1024)            ptype = received_packet[:1] #Type of packet                        #If it is hello packet            if ptype == b'H':                header = received_packet[:17]                payload = received_packet[17:].decode()                packet_type, ttl, source_ip, source_port, dest_ip, dest_port = struct.unpack("!cI4sH4sH",header)                                 neighborTimestamp[(socket.inet_ntoa(source_ip),source_port)] = time.time()                #If neighbor node is back to alive                 if not (socket.inet_ntoa(source_ip),source_port) in route_topology[cur_ip_port]:                    updateTopology(route_topology, cur_ip_port, socket.inet_ntoa(source_ip), source_port, update, True)                    forward_table = buildForwardTable(route_topology, cur_ip_port)                    generate_sendLink(emulator_socket, route_topology, cur_ip_port, sent_seq_no)                    sent_seq_no = sent_seq_no + 1                                #If it is Link State Pakcet                elif ptype == b'L':                    forwardpacket(emulator_socket, route_topology, forward_table, cur_ip_port, received_packet, neighborSequence, 'L')            elif ptype == b'T':                forwardpacket(emulator_socket, route_topology, forward_table, cur_ip_port, received_packet, {},'T')                                 except socket.error:            pass               #Check whether link is broken        for ip_port in route_topology[cur_ip_port]:            if time.time() - neighborTimestamp[ip_port] > 3:                #if link is broken, save that node to remove                update.append(ip_port)                #If there is/are something to update, remove the node and update topology and forward table        if(update):            update = updateTopology(route_topology, cur_ip_port, 0,0, update, False)            forward_table = buildForwardTable(route_topology, cur_ip_port)            generate_sendLink(emulator_socket, route_topology, cur_ip_port, sent_seq_no)            sent_seq_no = sent_seq_no + 1            """dij()    1. Using Dijkstra algorithm for building forward table"""def dij(graph, start):        distances = {node: float('infinity') for node in graph}    pred = {node: None for node in graph} #predecessors    distances[start] = 0    priority_queue = [(0, start)]    while priority_queue:        cur_dist, cur_node = heapq.heappop(priority_queue) #pop the distance and node        if cur_dist > distances[cur_node]:            continue        for neighbor in graph[cur_node]:            distance = cur_dist + 1  #Cost is always 1            if distance < distances[neighbor]: #if new distance is smaller, update                distances[neighbor] = distance                pred[neighbor] = cur_node                heapq.heappush(priority_queue, (distance, neighbor))    return distances, pred"""buildForwardTable()    1. build forward table    {(dest(ip, port): {'next_hop': (ip, port), 'cost': 1}"""def buildForwardTable(graph, node):    distances, pred = dij(graph, node)    routing_table = {}    for dest in graph:        if dest != node:            path = []            cur = dest            while cur is not None:                path.insert(0, cur) #add cur path                cur = pred[cur] #update cur            next_hop = path[1] if len(path) > 1 else None            routing_table[dest] = {'next_hop': next_hop, 'cost': distances[dest]}    return routing_tabledef main():    parser = argparse.ArgumentParser(description="emulator data")    parser.add_argument('-p', type=int, metavar='port', help= 'emulator port num')    parser.add_argument('-f', metavar='filename', help= 'name of topology file')    args = parser.parse_args()        #create socket object    try:        emulator_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    except:        print("Socket Error")        this_host = socket.gethostname()    this_ip_addr = socket.gethostbyname(this_host)    this_port = args.p    this_ip_port = (this_ip_addr, this_port)        emulator_socket.bind(this_ip_port)    emulator_socket.setblocking(0)        route_topology, forward_table = readtopology(this_ip_port, args.f, args.p)        createroutes(emulator_socket, this_ip_port, route_topology, forward_table)         if __name__ == "__main__":    main()