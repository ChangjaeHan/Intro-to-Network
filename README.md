# Intro-to-Network
학부 네트워크 수강하며 수행했던 프로젝트입니다. 
1. UDP 구현 2. UDP+Reliable Transfer+Emulator 구현 3. Link-state-routing protocol 구현


## 💻 P1 UDP Transfer 


●Packet type


<img width="412" alt="image" src="https://github.com/ChangjaeHan/Intro-to-Network/assets/83817116/06e823d2-7687-4496-958b-4464228e6562">


The sequence number is unsigned and must be converted to network byte order while being placed in the packet. 
For the sender, the sequence number can start at any arbitrary value, as specified by the user in the parameters. 
The sequence value increments with the number of "payload" bytes sent during a test. 
For Request packets, the sequence field is set to 0.

The length field is unsigned and specifies the number of bytes carried in the "payload" of the packet.
In case the packet type is a request, the packet length is set to 0.

The payload data is chunks from the file that the requester has requested. 
The sender chunks the file part that it has to payloads of the size that is identified by the length field in its parameters and sends them to the requester.
The last chunk can be of the size less than the length parameter based on how many bytes are left in the file.
No limit on the max size of the payload length.
The requester fills the payload field with the name of the file that it is requesting.


●Tracker
The tracker is a file (called tracker.txt). 
The tracker includes a table that will give the requester enough information to retrieve the file.
The table will have the following columns:
   Filename, ID, Sender_hostname, Sender_port

The first column is the file name.
The ID specifies the sequence at which the file parts should be retrieved. 
The next 2 fields specify the sender hostname and the port at which it is waiting to receive requests.
In each row the columns are separated by a single space and the end of each row is specified by an end-of-line character. 

file1.txt 2 mumble-01 5000
file2.txt 1 mumble-02 5000
file1.txt 1 mumble-03 6000
file1.txt 3 mumble-01 7000

2 senders can be on the same host as long as the port numbers on which they are waiting for requests are different.
Each time the requester is run, it refers to this table to figure out where it should retrieve the file from.


●Sender
The sender is invoked in the following way:

   python3 sender.py -p <port> -g <requester port> -r <rate> -q <seq_no> -l <length>

port is the port on which the sender waits for requests,
requester port is the port on which the requester is waiting,
rate is the number of packets to be sent per second,
seq_no is the initial sequence of the packet exchange,
length is the length of the payload (in bytes) in the packets.
Additional notes for the parameters:

sender and requester port sis in this range: 2049 < port < 65536
The sender will always send ‘D’ (Data) packets with the same payload length, except for perhaps the last packet of the transfer.
If the sender is responsible for 101 bytes of a file and has a length parameter set to 100, the second packet’s payload just contain the last byte of the file.
The sender will send an END packet after sending all its data packets.
The sender must print the following information for each packet sent to the requester, with each packet's information in a separate line.

The time that the packet was sent with millisecond granularity,
The IP of the requester,
The sequence number, and
The first 4 bytes of the payload


●Requester
The requester is invoked in the following way.

   python3 requester.py -p <port> -o <file option>

port is the port on which the requester waits for packets,
file option is the name of the file that is being requested.
The requester print the following information for each packet that it receives, with each packet's information in a separate line:

The time at which the packet was received in millisecond granularity,
Sender's IP address (in decimal-dot notation) and sender’s port number,
The packet sequence number,
The payload's length (in bytes), and
the first 4 bytes of the payload.
After the END packet is received, it should print the following summary information about the test separately for "each" sender:

Sender's IP address (in decimal-dot notation) and sender’s port number,
Total data packets received,
Total data bytes received (which should add up to the file part size),
Average packets/second, and
Duration of the test. This duration start with the first data packet received from that sender and end with the END packet from it.
The requester also write the chunks that it receives to a file with the same file name as it requested. This new file will be compared with the actual file that was sent out.





## 💻 P2 UDP+Reliable Transfer(Emulator, Window size of Data, TCP) 



The network emulator will receive a packet, decide where it is to be forwarded, and, based on the packet priority level, queue it for sending.
Upon sending, delay the packet to simulate link bandwidth, and randomly drop packets to simulate a lossy link.

Implement packet priority queues, a common feature of many packet queueing algorithms. 
There will be three packet priority levels, and there will be a separate sending queue for each priority level. Each queue will have a fixed size. 
If the outbound queue for a particular priority level is full, the packet will be dropped. Higher priority packets are always forwarded before lower priority packets.



●Packet type


<img width="849" alt="image" src="https://github.com/ChangjaeHan/Intro-to-Network/assets/83817116/a8d0ceeb-0ab5-48a8-8841-ccb4cf430df9">
8-bit priority, a 32-bit source IP address, a 16-bit source port, a 32-bit destination IP address, a 16-bit destination port and a 32-bit length

Valid values for priority levels are:
0x01 - highest priority
0x02 - medium priority
0x03 - lowest priority
For the ack packet, the packet type will be A (capital a) and the sequence field will contain the sequence number of the packet that is being acknowledged.
All the packets sent by the requester should have priority 1.
The priority of the END packet is the same as the other packets in the flow.



The logical functions of the emulator consist of routing, queueing, sending, and logging. Each sub-function is detailed below.

Static forwarding table:
The logical functions depend on the static forwarding table provided to the emulators through a file. The file contain lines in the format below, with space as delimiter between the various fields:

   <emulator> <destination> <nexthop> <delay> <loss probability>

emulator: a "<Host name> <Port>" pair that identifies the emulator for which the current entry is associated with. 
    Multiple emulators may be specified in a single table, and so they must filter only the lines that apply to them,
destination: a "<Host name> <Port>" pair that identifies the final destination of the packet,
next hop: a "<Host name> <Port>" pair that identifies the next entity to forward the packet to. It can be an emulator, sender or requester.
delay: in milliseconds, and identifies how long the emulator will delay before sending a packet to the corresponding destination.
loss probability: in percentage, and identifies the probability that the emulator will drop a packet when sending pockets to the corresponding destination.




Routing function:
The routing function is based on the static forwarding table. The destination of an incoming packet is compared with the destination in the forwarding table to find a match.
If a match is found, the packet is queued for forwarding to the next hop. 
If a match is not found, the packet is dropped and the event should be logged.

The emulator reads this file once it starts running and then only refers to its version of the file in memory for every packet. 
The emulator ignores lines in the table that do not correspond to its own hostname and port. 
Note that emulator, sender, and requester are all uniquely identified with a "<Host name, Port>" pair and thus multiple of them can run on the same host.


Queueing function:
The queueing function should examine the priority field on the packet and place the packet in an appropriate queue. All the three queues are of fixed size. This queue size is specified on the command line of the emulator startup. If a queue is full, the packet is dropped and this event is logged (see logging function below).


Send function:
The send function accepts packets from the three queues defined above and simulates network link conditions for each destination. 
Packets bound for a destination are first delayed to simulate link bandwidth. The delay is defined in the forwarding table and is specified in milliseconds.
After a packet has been delayed, it may be dropped to simulate a lossy link based on the loss probability provided in the forwarding table, and the event is logged.
If a packet is not dropped, it is then sent to the network.


Logging function:
The logging function is integral to all functions of the emulator. A packet may be dropped in the emulator in the routing function, the queueing function, or in the send function.
Any and all packet drop events must be logged to a file.
Loss events must provide a textual reason for the loss (e.g., "no forwarding entry found", "priority queue 1 was full'', "loss event occurred.")
Each log event must include the source hostname and port, the intended destination host name and port, the time of loss (to millisecond resolution), the priority level of the packet, and the size of the payload.




●Forwarding Summary
The order of processing should be similar to the following. 

1. Receive packet from network in a non-blocking way. This means that you should not wait/get blocked in the recvfrom function until you get a packet.
   Check if you have received a packet; If not jump to 4,
2. Once you receive a packet, decide whether packet is to be forwarded by consulting the forwarding table,
3. Queue packet according to packet priority level if the queue is not full,
4. If a packet is currently being delayed and the delay has not expired, goto Step 1.
5. If no packet is currently being delayed, select the packet at the front of the queue with highest priority, remove that packet from the queue and delay it,
6. When the delay expires, randomly determine whether to drop the packet,
7. Otherwise, send the packet to the proper next hop.
8. Goto Step 1.



●Reliable Transfer
The procedure is as follows:

1. Upon receipt of a request packet, the sender sends a full window of packets at the rate specified by the user.
2. The sender keeps this set of data in a buffer, and keeps a timeout for each of the packets.
    If it does not receive an ack for a packet and its timeout expires, it will retransmit that packet. The timeout is fixed and is specified by one of the sender's parameters.
3. If an ack packet is not received after re-transmitting the packet 5 times, the sender will print an error stating that it gave up on the packet with that specific sequence number, and continue with the next packet.
4. Once all packets of that window have been acked the sender sends another window of packets.
5. The requester should have a buffer and make sure that it saves the data to the file in the order of the packets' sequence numbers. It makes sure that it does not print duplicate packets into the file.
6. The requester acks every packet that it receives, even if it has already written that packet to the file (may happen if the sender retransmitted a packet due to its timeout, but the original packet actually made it to the requester).





●Emulator:

The network emulator is invoked in the following way:

python3 emulator.py -p <port> -q <queue_size> -f <filename> -l <log>

port: the port of the emulator.
queue_size: the size of each of the three queues.
filename: the name of the file containing the static forwarding table in the format specified above.
log: the name of the log file.
The network emulator must implement the routing, queueing, sending, and logging logical functions described above. It supports forwarding packets through one or multiple emulators (ex. sender to emulator1 to emulator2 to requester).

Note that your emulator should NOT drop END packets. This is because testing is made harder when END packets get dropped.


●Sender:

Note that the following requirements for your sender and requester are in addition to requirements stated for programming assignment 1.

Sender is invoked as follows:

python3 sender.py -p <port> -g <requester port> -r <rate> -q <seq_no> -l <length> -f <f_hostname> -e <f_port> -i <priority> -t <timeout>

f_hostname: the host name of the emulator.
f_port: the port of the emulator.
priority: the priority of the sent packets.
timeout: the timeout for retransmission for lost packets in the unit of milliseconds.
The behavior of the sender should be modified to:

Always start at sequence number 1
Increment the sequence number by 1 for each packet sent, instead of by the packet length
Print out the observed percentage of packets lost. The loss rate that the sender prints out is not necessarily the same as the loss rate that we identify in the forwarding table since the sender might miss some ACKs. This loss rate is computed by (number of retransmissions / total number of transmissions), where total number of transmissions including both normal transmissions and retransmissions.
The end packet is sent after ensuring that all data packets have been received by the receiver (or if max number of retries have reached for sending all packets in the last window).



●Requester:

Requester is invoked as follows:

python3 requester.py -p <port> -o <file option> -f <f_hostname> -e <f_port> -w <window>

f_hostname: the host name of the emulator.
f_port: the port of the emulator.
window: the requester's window size.

The inner length field of the request packet will be filled with this window size so that the sender can extract and use this value for sending.
Verify that the destination IP address in its received packet (data packets or end packets) is indeed its own IP address, and
Suppress display of individual DATA packet information.




Example:
<img width="720" alt="image" src="https://github.com/ChangjaeHan/Intro-to-Network/assets/83817116/79056b32-a0b2-428b-a60f-6ba80a2dd7fb">










## 💻P3 Link-state routing protocol 

Each node in the network is defined by an {IP,port} pair. 
After start-up, each emulator will implement the following functions: readtopology, createroutes, forwardpacket, and buildForwardTable.

readtopology will read a text file (topology.txt) which defines the interconnection structure of a test network that can have up to 20 nodes. 
The topology structure will be stored in a file and will have the following format:

IP_a,port_w IP_b,port_x IP_c,port_y IP_d,port_z …
IP_b,port_x IP_a,port_w IP_c,port_y IP_d,port_z …
...

The first {IP,port} pair in each line of the topology file corresponds to a node which is running an emulator and will be listening for packets from all of the remaining {IP,port} pairs in the line (ie. a one-way connection to the first node from all of the other nodes). The pairs are separated by a whitespace character. 




●Createroutes:

createroutes will implement a link-state routing protocol to set up a shortest path forwarding table between nodes in the specified topology. 
Through this function, each emulator should maintain the following datas:

1. The route topology containing the interconnection structure of the whole network.
2. The forwarding table containing entries in the form of (Destination, Nexthop), where Nexthop is the next node on the shortest path from current emulator to the destination. Both Destination and Nexthop are {IP, port} pairs. It is calculated by calling the buildForwardTable function with the route topology as the input, which will be described later.
3. The latest timestamp of the received HelloMessage from each of its neighbors. It will be a list of pairs (Neighbor, Timestamp).
4. The largest sequence number of the received LinkStateMessages from each node except itself. It will be a list of pairs (Node, Largest Seq No). 
5. The routing topology and the forwarding table must be updated if a node state change takes place. The createroutes function run continuously after the initial route topology and forwarding table have been specified by readtopology. It must be designed to react to nodes being responsive or unresponsive in the network and will require link-state information to be transmitted between an emulator and its neighbors.

The interval of transmission (ie. how frequently updates are sent) is up to you as is the mode of transport (TCP or UDP) and the link-state packet format. However you must ensure that your routing topology stabilizes within 5 seconds after a node state change takes place (For example when emulator 3 is died). 
The distance between neighbor nodes is 1 – weights on each link between nodes is 1.


Implement the "reliable flooding" algorithm where each node communicates only with its neighbors. 

1. HelloMessage: At defined intervals, each emulator should send the HelloMessage to its immediate neighbors. The goal of this message is letting the node know the state of its immediate neighbors.  
If a sufficiently long time passes without receipt of a “hello” from a neighbor, the link to that neighbor will be declared unavailable. 

Similarly, when handling the helloMessage coming from an unavailable neighbor, you should declare it available, update the route topology and forwarding table, and generate a new 
2. LinkStateMessage: At defined intervals, each emulator should send a LinkStateMessage to its immediate neighbors. It contains the following information:
- The (ip, port) pair of the node that created the message.
- A list of directly connected neighbors of that node, with the cost of the link to each one.
- A sequence number. Incremental by one each time the information b is updated and a new LinkStateMessage is generated. 
- A time to live (TTL) for this packet. 


3. Once receive a packet, decide the type of the packet. 

If it is a helloMessage, update the latest timestamp for receiving the helloMessage from the specific neighbor.
Check the route topology stored in this emulator. If the sender of helloMessage is from a previously unavailable node, change the route topology and forwarding table stored in this emulator. Then generate and send a new LinkStateMessage to its neighbors.
If it is a LinkSateMessage, check the largest sequence number of the sender node to determine whether it is an old message. If it’s an old message, ignore it. 
If the topology changes, update the route topology and forwarding table stored in this emulator if needed.
Call forwardpacket function to make a process of flooding the LinkStateMessage to its own neighbors.
If it is a DataPacket / EndPacket / RequestPacket in Lab 2, forward it to the nexthop. Don't need to do queueing, delaying and dropping.
If it is a routetrace packet (described below), refer to the routetrace application part for correct implementation.
4. Send helloMessage to all neighbors if a defined interval has passed since last time sending the helloMessage.

5. Check each neighbor, if helloMessage hasn’t received in time (comparing to the latest timestamp of the received HelloMessage from that neighbor), remove the neighbor from route topology, call the buildForwardTable to rebuild the forward table, and update the send new LinkStateMessage to its neighbors.

6. Send the newest LinkStateMessage to all neighbors if the defined intervals have passed.




●forwardpacket
forwardpacket will determine whether to forward a packet and where to forward a packet received by an emulator in the network. Be able to handle both packets regarding the LinkStateMessage, and packets that are forwarded to it from the routetrace application (described below). 
For LinkStateMessage, need to forward the LinkStateMessage to all its neighbors except where it comes from. 
However, when TTL (time to live) decreases to 0, don’t need to forward this packet anymore.


●buildForwardTable
buildForwardTable will use the forward search algorithm to compute a forwarding table based on the topology it collected from LinkStateMessage.
The forwarding table contains entries in the form of (Destination, Nexthop). 
Anytime an emulator node detects a change of its topology, it calls the buildForwardTable function to update its forwarding table.


●Emulator
The emulator will be invoked as follows:

  python3 emulator.py -p <port> -f <filename>

port: the port that the emulator listens on for incoming packets.
filename: the name of the topology file described above.




●Routetrace details
Routetrace is an application similar to the standard traceroute tool which will trace the hops along a shortest path between the source and destination emulators. routetrace will send packets to the source emulator with successively larger time-to-live values until the destination node is reached and will produce an output showing the shortest path to the destination. 

This application will generate an output that traces the shortest path between the source and destination node in the network that is given to it by the command line parameters below. An instance of routetrace will be invoked as follows:

   python3 trace.py -a <routetrace port> -b < source hostname> -c <source port> -d <destination hostname> -e <destination port> -f <debug option>

routetrace port: the port that the routetrace listens on for incoming packets.
source hostname, source port, destination hostname, destination port: routetrace will output the shortest path between the <source hostname, source port> to <destination hostname, destination port> .
Debug option: When the debug option is 1, the application will print out the following information about the packets that it sends and receives: TTL of the packet and the src. and dst. IP and port numbers. It will not do so when this option is 0.


Time to Live
Source IP, source port
Destination IP, destination port
More concretely here is what the routetrace application does:

It gets the (IP, port) of the source node and destination node from the command line.
It sets the TTL of the packet to 0: TTL=0
Send a routetrace packet to the source node with packet fields:
Time to Live: TTL, 
Source IP, source port: routetrace IP, routetrace Port     (from command line)
Destination IP, destination port: Destination IP, Destination Port (from command line)
Wait for a response.
Once it gets a response, print out the responders IP and port (that it gets from the response packet).
If the source IP and port fields of the routetrace packet that it received equals the destination IP and port from the command line then TERMINATES.
Otherwise, TTL = TTL + 1, goto 3.

If TTL is 0, create a new routetrace packet. Put its own IP and Port to the source IP and port fields of the routetraceReply packet. Other fields of the packet should be identical to the packet it received. Send that back to the routetrace application (using the source IP and port fields of the routetrace packet that it received).
If TTL is not 0, decrement the TTL field in the packet. Search in its route table and send the altered packet to the next hop on the shortest path to the destination.




●Example:

Topology: 

1.0.0.0,1 2.0.0.0,2 3.0.0.0,3
2.0.0.0,2 1.0.0.0,1 3.0.0.0,3 5.0.0.0,5
3.0.0.0,3 1.0.0.0,1 2.0.0.0,2 4.0.0.0,4
4.0.0.0,4 3.0.0.0,3 5.0.0.0,5
5.0.0.0,5 2.0.0.0,2 4.0.0.0,4

Forwarding table:

2.0.0.0,2 2.0.0.0,2
3.0.0.0,3 3.0.0.0,3
4.0.0.0,4 3.0.0.0,3
5.0.0.0,5 2.0.0.0,2

Consider the above topology. If we run the routetrace application between nodes 1 and 4, here is the output that the routetrace application should get:

Hop#  IP Port
1 1.0.0.0, 1
2 3.0.0.0, 3
3 4.0.0.0, 4

Now let's disable emulator 3 by using the command Ctrl + C. Routes should reconfigure. Within at most 5 seconds, the emulator with port 1 will print out the new topology and forwarding table:

Topology: 

1.0.0.0,1 2.0.0.0,2
2.0.0.0,2 1.0.0.0,1 5.0.0.0,5
4.0.0.0,4 5.0.0.0,5
5.0.0.0,5 2.0.0.0,2 4.0.0.0,4

Forwarding table:

2.0.0.0,2 2.0.0.0,2
4.0.0.0,4 2.0.0.0,2
5.0.0.0,5 2.0.0.0,2

Once we run the routetrace application again after a few seconds, we should get:

Hop#   IP, Port
1 1.0.0.0, 1
2 2.0.0.0, 2
3 5.0.0.0, 5
4 4.0.0.0, 4

