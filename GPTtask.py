# -*- coding: UTF-8 -*-

import socket
import openai
import json
import threading
from pydantic import BaseModel
from Messages import *

template_init_post = """{
    "role": "Initial info",
    "Purpose": "attacker's purpose",
    "system": "the system of the game"
}
"""

template_attack_post = """{
    "role": "attack",
    "id": "technic id from attack database",
    "message" : "other message"
}
"""

template_defence_post = """{
    "role": "defence",
    "id": "technic id from the engage database",
    "message" : "other message"
}
"""

template_response = """{
    "operation succeeded": "最后一项操作是否成功，如果最后一项操作是防守且成功防御某种攻击则为成功，如果为攻击者，成功发动攻击未被之前的防御行为防御则为成功，其余情况为失败",
    "reason": "如果最后一项操作失败了，结合演练信息和双方状态解释原因，没有失败则"None"(使用中文)",
    "info" : "如果最后一项操作成功且为攻击，则根据操作和预先生成的防御方信息返回攻击者应当获取到的防御者的具体信息、权限等，如果最后一项操作成功且为防御，则根据操和预先生成的防御方和攻击方信息作返回防御者操作的效果，如修补漏洞、发现攻击者行为等，不得使用“比如”等字眼，请根据上下文编造这些数据的具体内容(使用中文)",
    "attacker exposed": "True or False",
    "winner":"攻击者或者防守者",
}
"""

template_state = """{
    "role": "State",
    "info" : "a brief description of the state of the game",
    "prospect": "predict the outcome of the game and give brief explanation",
    "attacker exposed": "True or False",
    "attacker wins": "True or False",
    "defender wins": "True or False"
}
"""

test1 = '''
{
    "name": "Initial info",
    "Purpose": "get any file of the computer",
    "system": "windows XP"
}
'''

test2 = '''
{
    "ID" : "0001"
    "name": "attack",
    "id": "T1597"
}
'''

test3 = '''
{
    "ID" : "0002"
    "name": "attack",
    "technic id": "T1554"
}
'''

test4 = '''
{
    "ID" : "0004"
    "name": "defence",
    "technic id": "EAC0014"
}
'''

test5 = '''
{
    "ID" : "0004"
    "name": "defence",
    "technic id": "EAC0003"
}
'''

test_a = [test1, test2, "OP END"]
test_d = [test1, test4, test3, test2, test5, "OP END"]

messages = [{"role": "user", "content": "我们正在进行一个基于MITRE的网络攻防模拟演练"},
            # we are now playing a network attack and defense simulation game based on MITRE
            {"role": "user", "content": "我会首先告诉你双方的目的"},
            # I will first tell you the purpose of the attacker
            {"role": "user", "content": "攻击者与防御者的行为来自于MITRE的attack数据库以及engage模型"},
{"role": "user", "content": "你需要根据双方目的和信息预先自动生成攻击者与防御者的相关信息，如演练背景、服务器信息等"},
            # The behavior of the attacker and defender comes from the MITRE attack database and the engage model
            {"role": "user", "content": "我会按照操作顺序告知你攻击者或者防御者使用的技术在对应数据库中的编号"},
            # I will inform you of the number of the technology used by the attacker and the defender in the corresponding database
            {"role": "user", "content": "你需要根据所有操作来判断最后一步操作能否成功,如果不能,给出理由"},
            # You need to judge whether the operation chain of both parties can be established based on all the current operations, and if not, explain it
            {"role": "user", "content": "你需要根据所有的操作来判断攻击者是否达成目的，若达成目的告诉我攻击者获胜"},
            # You need to judge whether the attacker has achieved his goal based on all the operations, and if so, tell me that the attacker has won
            {"role": "user", "content": "你需要根据所有的操作来判断攻击者是否暴露"},
            # You need to judge whether the attacker has been exposed based on all the operations
            {"role": "user", "content": "当你认为攻击者难以达成目的时告诉我防御者获胜"},
            # When you think it is difficult for the attacker to achieve his goal, tell me that the defender wins
            {"role": "user",
             "content": "我会用以下格式给你信息" + template_init_post + template_attack_post + template_defence_post},
            # {"role": "user", "content": "每次操作后之需要回复OpSucceeded或者OpFailed"},

            {"role": "user", "content": "当我告知OP END时以" + template_response + "的格式回复我相关信息"},
            {"role": "user", "content": "严格输出json不能输出除json以外的内容，输出json时从{}开始不要额外标记"},
            {"role": "user", "content": "判断操作成功与否时，假定大多攻击行为建立在信息充足的前提下，既当防守方没有做出针对性防御行为前，皆为成功"},
            {"role": "user", "content": "判断操作成功与否时，上下文不足无法判断时，皆为成功"},
            {"role": "user", "content": "回复应当以面向最后一次操作的执行者（攻击方或防御方）的口吻回复，并除非在进行了相关操作的前提下，不得让操作者知晓对手的行为"},
            {"role": "user", "content": "严格按照我给的模板回复，包括对应的语言"},
            {"role": "user", "content": "回复应尽可能详细且符合逻辑，不得少于20字，不得以‘未提供攻击前提’‘信息不足无法判断’类似的话搪塞"},
            {"role": "user", "content": "明白之后请回复我ready to start"}]


def chat_with_gpt(op_link, API_KEY):
    openai.api_key = API_KEY
    openai.api_base = "https://key.wenwen-ai.com/v1"
    MODEL = "gpt-4"
    for i in op_link:
        mes = {"role": "user", "content": i}
        messages.append(mes)
    completion = openai.ChatCompletion.create(
        model=MODEL,
        messages=messages
    )
    answer = completion.choices[0].message.content
    return answer

# n = len(test_d)
# while True:
#
#     completion = openai.ChatCompletion.create(
#         model=MODEL,
#         messages=messages
#     )
#
#     chat_response = completion
#     answer = chat_response.choices[0].message.content
#     print(f"Response:\n {answer}")
#     messages.append({"role": "assistant", "content": answer})
#     # content = input("User: ")
#     for m in test_d:
#         messages.append({"role": "user", "content": m})
