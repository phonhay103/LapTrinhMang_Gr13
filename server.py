import socket, select

#Function to send message to all connected clients
def send_to_all (sock, message):
	#Message not forwarded to server and sender itself
	for socket in connected_list:
		if socket != server_socket and socket != sock :
			try :
				socket.send(message)
				print(message)
			except :
				# if connection not available
				socket.close()
				connected_list.remove(socket)

if __name__ == "__main__":
    # store message 
	name=""
	#to store address corresponding to username
	record={}
	# List to keep track of socket descriptors
	connected_list = []
	buffer = 4096
	port = 5001

	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	server_socket.bind(("127.0.0.1", port))
	server_socket.listen(10) #max 10 clients

	# Add server socket to the list of readable connections
	connected_list.append(server_socket)

	print ("\33[32m \t\t\t\tSERVER WORKING \33[0m") 

	while 1:
        # Get the list sockets which are ready to be read through select
		rList,wList,error_sockets = select.select(connected_list,[],[])

		for sock in rList:
			#connect new socket 
			if sock == server_socket:
				# Handle the case in which there is a new connection recieved through server_socket
				sockfd, addr = server_socket.accept()
				name = sockfd.recv(buffer)
				print(name + "\n")
				if name[:4] == "104 ":
					name = name[4:]
					connected_list.append(sockfd) # connected socket
					record[addr] = ""
				else:
					print("500 Error")
					sock.close()
				
                #if repeated username
				if name in record.values():
					sockfd.send("500 " + "\r\33[31m\33[1m Username already taken!\n\33[0m")
					del record[addr]
					connected_list.remove(sockfd)
					sockfd.close()
					continue
				else:
                    #add name and address
					record[addr]=name
					print("Client (%s, %s) connected" % addr," [",record[addr],"]")
					sockfd.send("105 Welcome to chat room. Enter 'tata' anytime to exit")
					print("105 Welcome to chat room. Enter 'tata' anytime to exit\n")
					send_to_all(sockfd, "105 "+name+" joined the conversation\n")

			#Some incoming message from a client
			else:
				# Data from client
				try:
					data1 = sock.recv(buffer)
					#print "sock is: ",sock
					if data1[:4] == "104 ":
						data = data1[:data1.index("\n")]
						data = data[4:]
						#print "\ndata received: ",data
                    	#get addr of client sending the message
						i,p=sock.getpeername()
						print(record[(i,p)] + " " +  data1)
						if data == "tata":
							msg = "105 " + "\r\33[1m"+"\33[31m "+record[(i,p)]+" left the conversation \33[0m\n"
							print(msg)
							send_to_all(sock,msg)
							print ("Client (%s, %s) is offline" % (i,p)," [",record[(i,p)],"]")
							del record[(i,p)]
							connected_list.remove(sock)
							sock.close()
							continue

					else:
						msg="105 \r\33[1m"+"\33[35m "+record[(i,p)]+": "+"\33[0m"+data+"\n"
						send_to_all(sock,msg)
            
                #abrupt user exit
				except:
					(i,p)=sock.getpeername()
					send_to_all(sock, "\r\33[31m \33[1m"+record[(i,p)]+" left the conversation unexpectedly\33[0m\n")
					print ("Client (%s, %s) is offline (error)" % (i,p)," [",record[(i,p)],"]\n")
					del record[(i,p)]
					connected_list.remove(sock)
					sock.close()
					continue

	server_socket.close()