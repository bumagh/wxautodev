from wxautox import WeChat
from wxautox.msgs import *
import time
import random
import threading
wx = WeChat()
wx.ChatWith("群游戏欢乐群")
sessions = wx.GetSession()
for session in sessions:
    if session.info['name']=="群游戏欢乐群":
        session.double_click()
        print(session.info)
        break
# # ses.double_click()
# chat = wx.GetSubWindow(nickname='群游戏欢乐群')
# print(chat.chat_type)
# print(chat.GetGroupMembers())