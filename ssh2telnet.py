import socketserver
import paramiko
import threading

# ssh settings
SSH_IP = '127.0.0.1'
SSH_PORT = 22
SSH_USER = 'xxxxxx'
SSH_PASSWD = 'xxxxxx'
# telnet share port
TELNET_PORT = 2222


clientlist = list()
sshshell = None


def sendtoall(msg):
    for cli in clientlist:
        cli.sendall(msg)


class MyTCPHandler(socketserver.BaseRequestHandler):
    def setup(self):
        print("{} connected".format(self.client_address))
        clientlist.append(self.request)

    def handle(self):
        while True:
            self.data = self.request.recv(1024)
            if len(self.data) == 0:
                break
            # print(self.data)
            sshshell.send(self.data)

    def finish(self):
        clientlist.remove(self.request)


def ssh_connect(sship, sshport, sshuser, sshpasswd):
    global sshshell
    sshclient = paramiko.SSHClient()
    sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    sshclient.connect(sship, sshport, sshuser, sshpasswd)
    sshshell = sshclient.invoke_shell()

    def ssh_proc():
        while True:
            data = sshshell.recv(1024)
            if len(data) == 0:
                break
            sendtoall(data)
    ssh_thread = threading.Thread(target=ssh_proc)
    ssh_thread.start()


if __name__ == "__main__":
    ssh_connect(SSH_IP, SSH_PORT, SSH_USER, SSH_PASSWD)
    with socketserver.ThreadingTCPServer(("localhost", TELNET_PORT), MyTCPHandler) as server:
        server.serve_forever()
