import socket
import ctypes
import time

#to receive data
host = "127.0.0.1"
port= 5001

client_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host, port))

user32= ctypes.windll.user32

def getKey(code):
    asciiTable= {
        "0": "[NULL]",
        "1": "[LCLICK]",

    }
    return asciiTable[code]