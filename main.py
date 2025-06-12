from wxautox import WeChat
from wxautox.msgs import *
import time
import random
import threading

           
                           
          
class WeChatBot:
    def __init__(self):
        self.wx = WeChat()
        print("微信初始化成功!")
        
        self.game_active = False
        self.current_group = ""
        self.players = []
        self.words = {}
        self.votes = {}
        self.game_thread = None
        self.official = "微游游戏官方"
        # 设置监听列表
        self.listen_list = [
            '微游游戏官方'
        ]
        
        # 启动游戏监听线程
        self.game_listener = threading.Thread(target=self.game_message_listener)
        self.game_listener.daemon = True
        self.game_listener.start()
    
    def game_message_listener(self):
        """监听游戏相关消息"""
        while True:
            if self.game_active:
                try:
                    # 获取游戏群的最新消息
                    self.wx.ChatWith(self.current_group)
                    msgs = self.wx.GetLastMessage
                    
                    if msgs:
                        sender, message = msgs[0], msgs[1]
                        
                        # 只处理玩家的消息
                        if sender in self.players:
                            if message.lower().startswith("投票"):
                                self.process_vote(sender, message)
                            elif message == "退出游戏":
                                self.players.remove(sender)
                                self.wx.SendMsg(f"{sender} 已退出游戏", self.current_group)
                except Exception as e:
                    print(f"游戏消息处理出错: {e}")
            
            time.sleep(1)
    
    def accept_friend_request(self, sender, message):
        """自动同意好友请求"""
        try:
            # 提取验证消息中的微信号
            wechat_id = ""
            if "微信号:" in message:
                wechat_id = message.split("微信号:")[-1].split("，")[0].strip()
            elif "wxid_" in message:
                wechat_id = message.split("wxid_")[-1].split(" ")[0].strip()
                wechat_id = "wxid_" + wechat_id
            
            if wechat_id:
                # 同意好友请求
                self.wx.AddFriend(wechat_id, verifyContent="自动通过")
                print(f"已同意 {wechat_id} 的好友请求")
                
                # 发送欢迎消息
                time.sleep(2)
                self.wx.ChatWith(sender)
                self.wx.SendMsg("👋 你好！我是微信机器人，已自动通过你的好友请求。发送'帮助'查看可用功能")
            else:
                print(f"无法提取微信号: {message}")
        except Exception as e:
            print(f"同意好友请求时出错: {e}")
    
    def create_group(self, who):
        """创建随机群聊"""
        try:
            # 获取好友列表
            self.wx.ChatWith(who="群游戏欢乐群", exact=False)
            friends = self.wx.GetGroupMembers()  # 取前5个好友
          #  nicknames = [item['昵称'] for item in friends]
           # print(friends)
            # print(nicknames)
            if len(friends) <= 3:
                random_selection = friends.copy()
            else:
                # 随机选择3个不重复的元素
                random_selection = random.sample(friends, 2)
            # if len(friends) < 3:
            #     self.wx.SendMsg("好友数量不足，无法创建群聊", who)
            #     return
            
            # 创建群聊
            group_name = f"欢乐谁是卧底群{random.randint(10000, 99999)}"
            self.wx.AddGroupMembers(group=self.official, members=random_selection)
            self.wx.ChatWith(who=group_name, exact=False)
            self.wx.ManageGroup(name=group_name)
            # 发送群公告
            # time.sleep(2)
            # self.wx.ChatWith(group_name)
            # self.wx.SendMsg("🎉 本群由机器人自动创建！")
            # self.wx.SendMsg("输入'谁是卧底'开始游戏，输入'帮助'查看其他功能")
            
            # 将新群添加到监听列表
            # if group_name not in self.listen_list:
            #     self.listen_list.append(group_name)
            #     self.wx.AddListenChat(who=group_name)
            
            # self.wx.SendMsg(f"已创建群聊: {group_name}", who)
            
        except Exception as e:
            print(f"创建群聊时出错: {e}")
            self.wx.SendMsg("创建群聊失败，请稍后再试", who)
    
    def start_game(self, group_name):
        """开始谁是卧底游戏"""
        if self.game_active:
            self.wx.SendMsg("游戏正在进行中，请稍后再试", group_name)
            return
        
        self.current_group = group_name
        self.game_active = True
        self.players = []
        self.votes = {}
        
        # 获取群成员
        try:
            members = self.wx.GetChatMembers(group_name)
            self.players = [m for m in members if m != self.wx.GetSelfName()]
            
            if len(self.players) < 3:
                self.wx.SendMsg("游戏需要至少3名玩家", group_name)
                self.game_active = False
                return
            
            # 准备游戏词汇
            word_pairs = [
                ("气泡", "水泡"),
                ("图书馆", "图书店"),
                ("保安", "保镖"),
                ("奥运会", "冬奥会"),
                ("沐浴露", "沐浴盐"),
                ("流星花园", "花样男子"),
                ("近视眼镜", "隐形眼镜"),
                ("十面埋伏", "四面楚歌"),
                ("遮阳帽", "棒球帽"),
                ("风油精", "清凉油"),
                ("矿泉水", "纯净水"),
                ("饼干", "酥饼"),
                ("领带", "领结"),
                ("蜡烛", "蜡笔"),
            ]
            
            civilian_word, undercover_word = random.choice(word_pairs)
            
            # 分配角色
            undercover_index = random.randint(0, len(self.players)-1)
            self.words = {}
            
            for i, player in enumerate(self.players):
                if i == undercover_index:
                    self.words[player] = undercover_word
                    role = "卧底"
                else:
                    self.words[player] = civilian_word
                    role = "平民"
                
                # 私聊发送词汇
                self.wx.ChatWith(player)
                self.wx.SendMsg(f"你的词汇是：{self.words[player]}（{role}）")
            
            # 群内发送游戏开始通知
            self.wx.ChatWith(group_name)
            self.wx.SendMsg("🎮 游戏【谁是卧底】开始！")
            self.wx.SendMsg(f"玩家数量：{len(self.players)}人（{len(self.players)-1}平民，1卧底）")
            self.wx.SendMsg("每人将收到私聊的词汇，描述时不要直接说出词汇！")
            self.wx.SendMsg("第一轮描述开始，请按顺序发言（每人限时30秒）")
            
            # 启动游戏线程
            self.game_thread = threading.Thread(target=self.run_game)
            self.game_thread.daemon = True
            self.game_thread.start()
            
        except Exception as e:
            print(f"启动游戏失败: {e}")
            self.wx.SendMsg("游戏启动失败，请稍后再试", group_name)
            self.game_active = False
    
    def run_game(self):
        """运行游戏主逻辑"""
        group = self.current_group
        round_num = 1
        
        try:
            while self.game_active and len(self.players) > 2:
                self.wx.ChatWith(group)
                self.wx.SendMsg(f"\n===== 第{round_num}轮 =====")
                
                # 玩家轮流描述
                for player in self.players[:]:
                    self.wx.SendMsg(f"请 {player} 描述你的词汇（30秒）")
                    time.sleep(30)
                
                # 投票环节
                self.wx.SendMsg("\n⚠️ 开始投票！请发送'投票 玩家名'（例如：投票 张三）")
                self.votes = {}
                time.sleep(60)  # 投票时间60秒
                
                # 统计投票
                vote_counts = {}
                for voter, voted in self.votes.items():
                    if voted in vote_counts:
                        vote_counts[voted] += 1
                    else:
                        vote_counts[voted] = 1
                
                # 找出得票最多的玩家
                if vote_counts:
                    max_votes = max(vote_counts.values())
                    candidates = [p for p, v in vote_counts.items() if v == max_votes]
                    
                    if len(candidates) == 1:
                        eliminated = candidates[0]
                        self.players.remove(eliminated)
                        word = self.words.get(eliminated, "未知")
                        
                        self.wx.SendMsg(f"🚫 {eliminated} 被淘汰出局！他的词汇是：{word}")
                        
                        # 检查游戏是否结束
                        if word != self.words[self.players[0]]:
                            self.wx.SendMsg(f"🎉 卧底被找出！平民获胜！")
                            self.game_active = False
                            break
                        else:
                            self.wx.SendMsg(f"😱 淘汰的是平民！游戏继续...")
                    else:
                        self.wx.SendMsg("⚠️ 平票！本轮无人淘汰")
                else:
                    self.wx.SendMsg("⚠️ 无人投票！本轮无人淘汰")
                
                round_num += 1
                time.sleep(5)
            
            if self.game_active:
                self.wx.SendMsg("🎮 游戏结束！卧底获胜！")
                self.game_active = False
        except Exception as e:
            print(f"游戏运行出错: {e}")
            self.wx.SendMsg("游戏出现错误，已终止", group)
            self.game_active = False
    
    def process_vote(self, voter, message):
        """处理投票"""
        try:
            parts = message.split()
            if len(parts) >= 2:
                voted_player = parts[1]
                if voted_player in self.players:
                    self.votes[voter] = voted_player
                    self.wx.ChatWith(voter)
                    self.wx.SendMsg(f"✅ 你已投票给：{voted_player}")
        except:
            pass
    
    def show_help(self, who):
        print(f"show_help: {who}")
        help_msg = """
🤖 微信机器人帮助：
1. 创建群聊 - 自动创建随机群聊
2. 谁是卧底 - 在群内开始文字版游戏
3. 退出游戏 - 在游戏进行中退出
4. 帮助 - 显示此帮助信息

游戏规则：
- 每人会收到一个词汇（卧底词汇与其他人不同）
- 每轮每人描述自己的词汇（不要直接说出词汇）
- 投票淘汰可疑的卧底
- 找出卧底则平民获胜，卧底坚持到最后则卧底获胜
        """
        self.wx.SendMsg(help_msg,who=self.official)
        """显示帮助信息"""
       
      
    def on_msg(self,msg,chatname):
        time.sleep(len(msg.content))
        print(f"收到来自 {chatname} 的消息: {msg.content}")
        if isinstance(msg, FriendMessage):                 
            if msg.content == "创建群聊":
                 self.create_group(chatname)
            elif msg.content == "谁是卧底":
                self.start_game(chatname)
            elif msg.content == "帮助": 
                self.show_help(chatname)
    def run(self):
        """运行主监听循环"""
        # 循环添加监听对象
        self.wx.AddListenChat(nickname="微游游戏官方",callback=self.on_msg)
        self.wx.KeepRunning()

if __name__ == "__main__":
    bot = WeChatBot()
    bot.run()