# -*- coding: UTF-8 -*-

import socket
import time
import sys
import openai
import json
from threading import Thread
from time import sleep
from Messages import *
from GPTtask import *
from pydantic import BaseModel
import re

# KEY = sys.argv[1]
KEY = "sk-qSb1I1n9J9TRWd1G96B513779aB84dAeAa3720BaBe4152C5"
print("使用API key:" + KEY)


# test1 = '''{
#     "name": "Initial info",
#     "Attacker's Purpose": "get any file of the computer",
#     "Defender's Purpose": "get any file of the computer"，
#     "system": "windows XP"
# }'''
#
# test2 = '''{
#     "ID" : "0001"
#     "name": "attack",
#     "technic id": "T1595.0001"
# }'''
#
# test3 = '''{
#     "ID" : "0002"
#     "name": "attack",
#     "technic id": "T1650"
# }'''
#
# test3 = '''{
#     "ID" : "0003"
#     "name": "attack",
#     "technic id": "T1133"
# }'''


def addd(dic1, dic2):
    sum_dic = {}
    for key in dic1:
        sum_dic[key] = dic1[key]
    for key in dic2:
        sum_dic[key] = dic2[key]
    return sum_dic


test = [test1, test2, test3, "OP END", "State"]

rec_s = socket.socket()
host = "127.0.0.1"
port = 8082
rec_s.connect((host, port))
print(f"接收通道已连接至{host}:{port}")
op_link = []
mes_tail = ["OP END", "State"]

send_s = socket.socket()
send_host = "127.0.0.1"
send_port = 8083
send_s.bind((send_host, send_port))
send_s.listen(1000)
c, addr = send_s.accept()
print(f"发送通道已连接至{addr[0]}:{send_port}")


def send_mes(Message):
    c.send(Message.encode())
    send_s.close()
    print(f"发出:\n{Message}")


class SendThread(Thread):
    def __init__(self, func, args):
        Thread.__init__(self)
        self.func = func
        self.args = args

    def run(self):
        self.func(*self.args)


def send_message(Message):
    sendTask = SendThread(send_mes, (Message,))
    sendTask.start()
    sendTask.join()
    return


init = {"name": "Initial info", "Attacker's purpose": "获取防守方信息"}
acts = [
    # {"role":"attack","id":"T1598","message":""}
]
test22 = """action
{"role":"attack","id":"T1597","message":""}"""
while True:
    recv = rec_s.recv(5120).decode('utf-8')
    print(f"收到:\n{recv}")
    reobj = re.match(r'^(\w+)\s*(?=\{)([\w\W]*)', recv)

    if reobj.group(1) == "reset":
        acts = []
        init = {"name": "Initial info"}
        continue

    if reobj.group(1) == "init":
        init_info = json.loads(reobj.group(2))

        if init_info["role"] == "attack":
            init["Attacker's purpose"] = init_info["purpose"]

        elif init_info["role"] == "defense":
            init["Defender's purpose"] = init_info["purpose"]

        else:
            init["Attacker's purpose"] = "get full property of a certain file"
            init["Defender's purpose"] = "prevent the attacker from getting full property of a certain file"
        init["system"] = "Ubuntu 20.04LTS"
        continue

    recv = reobj.group(2)
    recv_dic = json.loads(recv)
    role = recv_dic["role"]
    aid = recv_dic["id"]
    act = {"role": recv_dic["role"], "id": recv_dic["id"], "message": recv_dic["message"]}
    acts.append(json.dumps(act))
    # recv = recv.split('\n')[1]
    out = chat_with_gpt([json.dumps(init)] + acts + ["OP END"], KEY)
    out_obj = re.search((r'(\{.*\})'), out, re.S | re.M)
    print(f"MODEL REPLY:\n{out}")
    reply = json.loads(out_obj.group(0))
    head = {"role": role, "id": aid}
    out = json.dumps(addd(head, reply))
    send_message(out)
    isSucceed = 1
    # isSucceed = 0
    # while isSucceed == 0:
    #     try:
    #         out = chat_with_gpt([json.dumps(init)] + acts + ["OP END"], KEY)
    #         out_obj = re.search((r'(\{.*\})'), out, re.S | re.M)
    #         print(f"MODEL REPLY:\n{out}")
    #         reply = json.loads(out_obj.group(0))
    #         head = {"role": role, "id": aid}
    #         out = json.dumps(addd(head, reply))
    #         send_message(out)
    #         isSucceed = 1
    #     except:
    #         print('ERROR: MODEL REPLY ERROR  AUTO: TRY AGAIN')
    #         continue

    # while len(pool) >= 0:
    #     # messages.append(pool.pop(0))
