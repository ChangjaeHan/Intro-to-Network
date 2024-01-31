#Changjae Hanimport selectimport socketimport structimport argparseimport datetime as dtimport time"""Request_data    1. Create the requester and the sender socket    2. Pack the packet    3. Send it to the sender"""def request_data(req_port, file_option, emulator_name, emulator_port, window_size, row, is_first):    #Create a requester socket for UDP transmission    requester_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    requester_socket.setblocking(0) #Non-blocking        requester_ip_addr = socket.gethostbyname(socket.gethostname())    requester_addr_port = (requester_ip_addr, req_port)    #Bind the socket to the requester's address    requester_socket.bind(requester_addr_port)            #Create a sender socket for UDP transmission    sender_ip_addr = socket.gethostbyname(row[2])    sender_addr_port = (sender_ip_addr, int(row[3]))        emulator_ip_addr = socket.gethostbyname(emulator_name)     emulator_addr_port = (emulator_ip_addr, emulator_port)                    #Request packet    #Create packet inner header      inner_header_info = struct.pack("!cII", b'R', 0, window_size)     #Create packet outer header    size_of_inner = struct.calcsize("!cII")    outer_header_info = struct.pack("!B4sH4sHI", 1, socket.inet_aton(requester_ip_addr), req_port, socket.inet_aton(sender_ip_addr), int(row[3]), size_of_inner)        #Combine packet header with payload    packet = outer_header_info + inner_header_info + row[0].encode()    #Send the request packet to the emulator    requester_socket.sendto(packet, emulator_addr_port)        #Processing received data    process_data(file_option, is_first, requester_socket, requester_ip_addr, req_port, emulator_addr_port)                """Process_data    1. Process the received data by unpacking    2. Send ACK when received    2. Calculate time and bytes    3. Write the data to the file"""def process_data(file_option, is_first, requester_socket, requester_ip_addr, req_port, emulator_addr_port):        sum_bytes = 0    sum_packets = 0    ptype = {b'D':"DATA", b'E':"END"}        #Check if it's first data    if is_first:        file = open(file_option, "w")    else:         file = open(file_option, "a")        requester_buffer = []    #When the requester gets data from the sender    while True:        check_time = time.time()        readable, _, _ = select.select([requester_socket], [], [], 0) #Non-blocking        if requester_socket in readable:            try:                received_packet,(ip,port) = requester_socket.recvfrom(1024)            except socket.error:                continue                            wait_time = time.time()            packet_time = round(wait_time - check_time)                        #Classify header and payload            outer_header = received_packet[:17]            inner_header = received_packet[17:26]                        decoded_outer_header = struct.unpack("!B4sH4sHI", outer_header)            decoded_inner_header = struct.unpack("!cII", inner_header)            prior, got_src_addr, got_src_port, got_dest_addr, got_dest_port, outer_length = decoded_outer_header             packet_type, seq_no, length = decoded_inner_header                        #Print out packet information received             print(ptype[packet_type] + " Packet")            print("recv time:  ", dt.datetime.now(), sep='')            print("sender addr:  ", socket.inet_ntoa(got_src_addr), ":", got_src_port, sep='')            print("sequence:  ", socket.ntohl(seq_no))            print("length:  ", length)                        sum_bytes += length                        #If packet type is DATA and verify the address and port            if packet_type == b'D' and got_dest_port == req_port and socket.inet_ntoa(got_dest_addr) == requester_ip_addr:                 if socket.ntohl(seq_no) not in requester_buffer:                    payload = received_packet[26:]                    print("This is a DATA packet")                    print("get dest_port this will be src:",got_dest_port)                    print("get src_port this will be dest:",got_src_port)                    sum_packets += 1                    file.write(payload.decode())                    print("payload is ", payload.decode())                                        #For ACK packet                    inner_header_info = struct.pack("!cII", b'A', seq_no, length)                     #Create packet outer header                    size_of_inner = struct.calcsize("!cII")                    outer_header_info = struct.pack("!B4sH4sHI", 1, got_dest_addr, got_dest_port, got_src_addr, got_src_port, size_of_inner)                       #Combine packet header with payload                    packet = outer_header_info + inner_header_info + payload                    requester_socket.sendto(packet, emulator_addr_port)                    requester_buffer.append(socket.ntohl(seq_no))            elif packet_type == b'E': #END                print("")                print("*****END PACKET ARRIVE*****")                print("")                print("Summary")                print("sequence: ", socket.ntohl(seq_no))                print("sender addr:  ", socket.inet_ntoa(got_src_addr), ":", got_src_port, sep='')                print("Total Data packets:  ", sum_packets, sep='')                print("Total Data bytes:  ", sum_bytes, sep='')                print("Average packets/second:  ", packet_time, sep='')                break            file.close()    requester_socket.close()def main():    parser = argparse.ArgumentParser(description="requester data")    parser.add_argument('-p', type=int, metavar='port', help= 'requester port num')    parser.add_argument('-o', metavar='file_option', help= 'filename')    parser.add_argument('-f', metavar='f_hostname', help= 'host name of emulator')    parser.add_argument('-e', type=int, metavar='f_port', help= 'port of emulator')    parser.add_argument('-w', type=int, metavar='window', help= "requester's window size")    args = parser.parse_args()    is_first = True        tracker_file = open("tracker.txt", "r")        #Tracket_list to handle the order and unrelavant files    tracker_list = []    while True:        cur_line = tracker_file.readline()        if not cur_line: break        each_data = cur_line.split(" ")        each_data[-1] = each_data[-1].strip() #Remove each space in the end of cur_line        tracker_list.append(each_data)            #Sorted by num not to find the order over the list    tracker_list = sorted(tracker_list, key=lambda t: t[1])    print("Requester's print information")    print("-----------------------------------------------------------------------------")            for row in tracker_list:        if row[0] == args.o:#if it is requested file            startTime = time.perf_counter()            request_data(args.p, args.o, args.f, args.e, args.w, row, is_first)            endTime = time.perf_counter()            print("Duration of the test:  ", round((endTime-startTime)*1000), " ms", sep='')            print("")            is_first = False     print("")    print("-----------------------------------------------------------------------------")    print("In addition, a file ", args.o, " will be generated in the directory requester/.", sep='')     print("The content should be:")    print("")        with open(args.o, encoding="UTF8") as data :        contents = data.read()        print(contents)        print("")    print("-----------------------")        if __name__ == "__main__":    main()