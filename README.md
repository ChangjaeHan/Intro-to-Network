# Intro-to-Network


//////////////////////////
#P1 UDP Transfer


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





//////////////////////////
#P2 UDP+Reliable Transfer(Emulator, Window size of Data, TCP)





//////////////////////////
#P3 Link-state routing protocol
