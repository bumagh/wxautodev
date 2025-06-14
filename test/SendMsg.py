from wxautox import WeChat
from wxautox.msgs import *
import time
import random
import threading
wx = WeChat()
wx.SendMsg("hello",who="群游戏欢乐群")