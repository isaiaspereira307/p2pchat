import socket
import struct
import threading
import time
import fcntl
from Tkinter import *

class Client:
    def __init__(self, _IP, _ID):
        self.ID = _ID
        self.IP = _IP
        self.TTL = 30
    def __str__(self):
        return "ID = {0}\tIP:PORTA = {1}\tTTL={3} ".format(self.ID,self.IP,self.TTL)
    def resetTTL(self):
        self.TTL = 30
    def decrementaTTL(self):
        time.sleep(1)
        self.TTL -= 1
    def getIP(self):
        return self.IP
    def getPort(self):
        return self.Port
    def getID(self):
        return self.ID
    def getTTL(self):
        return self.TTL

client_list = []
nick = ""
sair = 0

MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007
CHAT_PORT = 8001
MY_IP = get_ip_address('wlan0')

def pertence(lista,filtro):
    i=0
    for x in lista:
        if filtro(x):
            return True,i
        i+=1
    return False,-1

def main():
    nick = raw_input("Digite seu nick: ")
    thr1 = threading.Thread(target = mcast_rcv)
    thr1.start()

    thr2 = threading.Thread(target = mcast_hello)
    thr2.start()
    
    thr3 = threading.Thread(target = client_loop)
    thr3.start()

def mcast_rcv():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((MCAST_GRP, MCAST_PORT))  # use MCAST_GRP instead of '' to listen only
                                                            # to MCAST_GRP, not all groups on MCAST_PORT
    mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)

    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    while not sair:
        data, addr =  sock.recvfrom(1024)
        # print data, "from: ",  addr
        cliente = Client(addr[0],data)
        existe, posicao = pertence (client_list,lambda x: x.IP == cliente.IP)
        if not existe: 
            client_list.append(cliente)
        else:
            client_list[posicao].resetTTL()

def mcast_hello():
    while not sair:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        sock.sendto(nick, (MCAST_GRP, MCAST_PORT))
        time.sleep(5);

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(),0x8915,struct.pack('256s', ifname[:15]))[20:24])

def client_loop():
    global sair
    while not sair:
        print "\nOla {0}\n".format(nick)
        print "1.Mostrar lista de clientes\n"
        print "2.Mandar mensagem\n"
        print "0.Sair\n"
        opcao = int(input("Insira uma opcao : "))
        if(opcao==0):
            sair = 1
        elif(opcao==1):
            for x in client_list:
                print x
        elif(opcao==2):
            who = raw_input("Para quem mandar a mensagem?")
            existe, posicao = pertence(client_list, lambda x: x.ID == who)
            if existe:
                msg = raw_input("Insira sua mensagem : ")
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
                sock.sendto(msg, (client_list[posicao].getIP(),CHAT_PORT))
            else:
                print "Erro! Usuario nao existente.\n"

if __name__ == "__main__":
    main()
    # print get_ip_address('wlan0')
    # root = Tk()
    # S = Scrollbar(root)
    # T = Text(root, height = 4, width=50)
    # S.pack(side=RIGHT, fill=Y)
    # T.pack(side=LEFT,fill=Y)
    # S.config(command=T.yview)
    # T.config(yscrollcommand=S.set)
    # quote = """HAMLET: To be, or not to be--that is the question: 
    # Whether 'tis nobler in the mind to suffer
    # The slings and arrows a sea of troubles
    # And bt opposing end them. To die, to sleep--
    # No more--and by a sleep to say we end
    # The heartache, and the thousand natural shocks
    # that flesh is heir to. 'Tis a consummation
    # Devoutly to be wished."""
    # T.pack()
    # T.insert(END,quote)
    # T.pack()
    # T.insert(END,"oi")
    # root.mainloop()
