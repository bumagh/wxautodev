from wxautox import WeChat
from wxautox.msgs import *
import time
import random
import threading
import json
import os
import traceback          
class WeChatBot:
    def __init__(self):
        self.wx = WeChat()
        print("微信初始化成功!")
        
        self.game_active = False
        self.selfnickname = ''
        self.TeamMax=4
        self.current_group = "群游戏欢乐群"
        self.sub_group = ""
        self.original_players=[]
        self.players = []
        self.word_pairs = []
        self.civilian_word=""
        self.undercover_word=""
        self.words = {}
        self.votes = {}
        # self.player_scores = {}  # 存储玩家积分 {玩家名: 积分}
        self.scores_file = "player_scores.json"  # 积分存储文件
        self.player_scores = self.load_scores()  # 从文件加载积分
         # 准备大厅系统
        self.lobby_queues = {}  # {群名: [已准备玩家列表]}
        self.lobby_status = {}  # {群名: 最后活跃时间}
        self.lobby_timeout = 300  # 5分钟无活动自动清空大厅
        self.roles = {}  # 存储玩家角色 {玩家名: "平民"或"卧底"}
        self.current_group_chat = {}
        self.current_group_session = {}
        self.game_thread = None
        self.official = "AAA赣州郭"
        # self.official = "微游游戏官方"
        # 设置监听列表
        self.listen_list = [
            self.official
        ]
        with open('word_pairs.json', 'r', encoding='utf-8') as f:
            self.word_pairs = json.load(f)['word_pairs']
        # print(self.word_pairs)
        # 启动游戏监听线程
        # self.game_listener = threading.Thread(target=self.game_message_listener)
        # self.game_listener.daemon = True
        # self.game_listener.start()
        # 启动大厅管理线程
        # self.lobby_manager = threading.Thread(target=self.manage_lobbies)
        # self.lobby_manager.daemon = True
        # self.lobby_manager.start()
    def manage_lobbies(self):
        """管理准备大厅，清理超时大厅"""
        while True:
            current_time = time.time()
            to_remove = []
            
            for lobby, last_active in self.lobby_status.items():
                if current_time - last_active > self.lobby_timeout:
                    to_remove.append(lobby)
            
            for lobby in to_remove:
                if lobby in self.lobby_queues:
                    del self.lobby_queues[lobby]
                if lobby in self.lobby_status:
                    del self.lobby_status[lobby]
                print(f"清理超时大厅: {lobby}")
            
            time.sleep(60)  # 每分钟检查一次
    def load_scores(self):
        """从文件加载积分数据"""
        try:
            if os.path.exists(self.scores_file):
                with open(self.scores_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"加载积分文件失败: {e}")
            return {}
    
    def save_scores(self):
        """保存积分数据到文件"""
        try:
            with open(self.scores_file, 'w', encoding='utf-8') as f:
                json.dump(self.player_scores, f, ensure_ascii=False, indent=2)
            print("积分数据已保存")
        except Exception as e:
            print(f"保存积分文件失败: {e}")
    def game_message_listener(self,msg,chat):
        chatname = chat.ChatInfo()['chat_name']
        """监听游戏相关消息"""
        if True:
                try:
                    #获取游戏群的最新消息
                #     msgs = self.wx.GetLastMessage
                    if msg.type=='text':
                            sender, message = msg.sender, msg.content
                            # 只处理玩家的消息
                            if sender in self.players:
                                if message.lower().startswith("投"):
                                    self.process_vote(sender, message)
                                elif message == "退出游戏":
                                    self.players.remove(sender)
                                    self.wx.SendMsg(f"{sender} 已退出游戏", self.current_group)
                            # 处理准备状态命令
                            if message == "准备状态":
                                if chatname in self.lobby_queues:
                                    count = len(self.lobby_queues[chatname])
                                    players = "\n".join(self.lobby_queues[chatname])
                                    self.wx.SendMsg(f"当前准备人数: {count}/{self.TeamMax}\n准备玩家:\n{players}", chatname)
                                else:
                                    self.wx.SendMsg("当前没有准备中的玩家", chatname)
                            if message == "再来一局":
                                self.start_game(self.sub_group)
                except Exception as e:
                    print(f"游戏消息处理出错: {e}")
                    error_trace = traceback.format_exc()
                    print(f"游戏消息处理出错: \n{error_trace}")
    def on_main_group_msg(self,msg,chat):
        chatname = chat.ChatInfo()['chat_name']
        """监听游戏相关消息"""
        if True:
                try:
                    #获取游戏群的最新消息
                #     msgs = self.wx.GetLastMessage
                    if msg.type=='text':
                            sender, message = msg.sender, msg.content
                            # 只处理玩家的消息
                            if sender in self.players:
                                if message.lower().startswith("投"):
                                    self.process_vote(sender, message)
                                elif message == "退出游戏":
                                    self.players.remove(sender)
                                    self.wx.SendMsg(f"{sender} 已退出游戏", self.current_group)
                             # 处理准备大厅命令
                            if message in ["准备", "取消准备"]:
                                    self.manage_lobby(chatname, sender, message)

                            # 处理准备状态命令
                            if message == "准备状态":
                                if chatname in self.lobby_queues:
                                    count = len(self.lobby_queues[chatname])
                                    players = "\n".join(self.lobby_queues[chatname])
                                    self.wx.SendMsg(f"当前准备人数: {count}/{self.TeamMax}\n准备玩家:\n{players}", chatname)
                                else:
                                    self.wx.SendMsg("当前没有准备中的玩家", chatname)
                except Exception as e:
                    print(f"游戏消息处理出错: {e}")
                    error_trace = traceback.format_exc()
                    print(f"游戏消息处理出错: \n{error_trace}")
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
    
    def create_group(self, group, players=None):
        """创建随机群聊"""
        print('创建群中：列表：')
        print(players)
        try:
             # 如果没有指定玩家，随机选择好友
            if players is None:
                # 获取好友列表
                self.wx.ChatWith(who="群游戏欢乐群", exact=False)
                friends = self.wx.GetGroupMembers()  # 取前5个好友
            #  nicknames = [item['昵称'] for item in friends]
            # print(friends)
                # print(nicknames)
                if len(friends) <= 3:
                    players = friends.copy()
                else:
                    # 随机选择3个不重复的元素
                    players = random.sample(friends, 2)
            # if len(friends) < 3:
            #     self.wx.SendMsg("好友数量不足，无法创建群聊", who)
            #     return
            
            # 创建群聊
            group_name = f"欢乐谁是卧底群{random.randint(10000, 99999)}"
            self.sub_group = group_name
            self.wx.AddGroupMembers(group=self.official, members=players)
            self.wx.ChatWith(who=group_name, exact=False)
            self.wx.ManageGroup(name=group_name)
            # 发送群公告
            # time.sleep(2)
            # self.wx.ChatWith(group_name)
            self.wx.SendMsg("🎉 本群由机器人自动创建！")
            self.wx.AddListenChat(nickname=self.sub_group,callback=self.game_message_listener)
            # self.wx.SendMsg("输入'谁是卧底'开始游戏，输入'帮助'查看其他功能")
            # 将新群添加到监听列表
            # if group_name not in self.listen_list:
            #     self.listen_list.append(group_name)
            #     self.wx.AddListenChat(who=group_name)
            
            # self.wx.SendMsg(f"已创建群聊: {group_name}", who)
            
        except Exception as e:
            print(f"创建群聊时出错: {e}")
            # self.wx.SendMsg("创建群聊失败，请稍后再试", who=group)
    
    def start_game(self, group_name):
        """开始谁是卧底游戏"""
        if self.game_active:
            self.wx.SendMsg("游戏正在进行中，请稍后再试", who=group_name)
            return
        print(group_name)
        self.wx.ChatWith(group_name,exact=True)
        self.game_active = True
        self.players = []
        self.votes = {}
        
        # 获取群成员
        try:
            sessions = self.wx.GetSession()
            for session in sessions:
                if session.info['name']==group_name:
                    session.double_click()
                    self.current_group_session=session
                    break
            chat = self.wx.GetSubWindow(nickname=group_name)
            self.current_group_chat = chat
            members = chat.GetGroupMembers()
            self.players = [m for m in members if m != self.selfnickname]
            #
            # self.players = members
            
            # if len(self.players) < 3:
            #     self.wx.SendMsg("游戏需要至少3名玩家")
            #     self.game_active = False
            #     return
            
            # 准备游戏词汇
       
            civilian_word, undercover_word = random.choice(self.word_pairs)
           
            # 分配角色
            undercover_index = random.randint(0, len(self.players)-1)
            self.words = {}
            self.roles = {}  # 重置角色记录
            
            for i, player in enumerate(self.players):
                if i == undercover_index:
                    self.words[player] = undercover_word
                    role = "卧底"
                else:
                    self.words[player] = civilian_word
                    role = "平民"
                # 记录玩家角色
                self.roles[player] = role
                # 私聊发送词汇
                self.wx.SendMsg(f"你的词汇是：{self.words[player]}（{role}）",who=player)
                time.sleep(2)
            # 群内发送游戏开始通知
            time.sleep(1)
            self.wx.SendMsg("🎮 游戏【谁是卧底】开始！",who=group_name)
            self.show_scoreboard(group_name)

            self.wx.SendMsg(f"玩家数量：{len(self.players)}人（{len(self.players)-1}平民，1卧底）",who=group_name)
            self.wx.SendMsg("每人将收到私聊的词汇，描述时不要直接说出词汇，含蓄一点，禁止拼音！",who=group_name)
            self.wx.SendMsg("第一轮描述开始，请大家同时发言（25秒）",who=group_name)
            
            # 启动游戏线程
            self.game_thread = threading.Thread(target=self.run_game)
            self.game_thread.daemon = True
            self.game_thread.start()
            
        except Exception as e:
            print(f"启动游戏失败: {e}")
            self.wx.SendMsg("游戏启动失败，请稍后再试", who=group_name)
            self.game_active = False
    
    def run_game(self):
        """运行游戏主逻辑"""
        group = self.current_group
        round_num = 1
        self.original_players = self.players[:]  # 保存原始玩家列表
        try:
            while self.game_active and len(self.players) > 2:
                self.wx.SendMsg(f"\n===== 第{round_num}轮 =====",who=self.sub_group)

                player_list = list(enumerate(self.players, start=1))
                player_info = "\n".join([f"{num}. {player}" for num, player in player_list])
                self.wx.SendMsg(f"当前玩家列表：\n{player_info}",who=self.sub_group)
                # 玩家轮流描述
                # for player in self.players[:]:
                #     self.wx.SendMsg(f"请 {player} 描述你的词汇（15秒）",who=self.current_group)
                #     time.sleep(15)
                time.sleep(25)
            
                # 投票环节
                self.wx.SendMsg(f"当前玩家列表：\n{player_info}",who=self.sub_group)
                self.wx.SendMsg("\n⚠️ 开始投票(投票时间12秒)！请通过数字投票（例如：投 1）中间用空格分隔",who=self.sub_group)

                self.votes = {}
                time.sleep(12)  # 投票时间60秒
                 # 重新生成玩家编号列表（可能有玩家退出）
                player_list = list(enumerate(self.players, start=1))
                vote_list = "\n".join([f"{num}. {player}" for num, player in player_list])
                self.wx.SendMsg(f"投票列表：\n{vote_list}", who=self.sub_group)
               
                # 统计投票
                vote_counts = {}
                for voter, vote_data in self.votes.items():
                    # vote_data 包含 (投票数字, 玩家名)
                    voted_player = vote_data[1]
                    if voted_player in vote_counts:
                        vote_counts[voted_player] += 1
                    else:
                        vote_counts[voted_player] = 1
                 # 显示每个人的投票结果
                if self.votes:
                    vote_results = []
                    for voter, vote_data in self.votes.items():
                        vote_num, voted_player = vote_data
                        vote_results.append(f"{voter} → {voted_player} (编号 {vote_num})")
                    
                    result_msg = "📊 投票结果：\n" + "\n".join(vote_results)
                    self.wx.SendMsg(result_msg, who=self.sub_group)
                else:
                    self.wx.SendMsg("⚠️ 本轮无人投票", who=self.sub_group)
                # 找出得票最多的玩家
                if vote_counts:
                    max_votes = max(vote_counts.values())
                    candidates = [p for p, v in vote_counts.items() if v == max_votes]
                      # 显示票数统计
                    count_msg = "📊 得票统计：\n" + "\n".join([f"{player}: {count}票" for player, count in vote_counts.items()])
                    self.wx.SendMsg(count_msg, who=self.sub_group)
                    if len(candidates) == 1:
                        eliminated = candidates[0]
                        self.players.remove(eliminated)
                        word = self.words.get(eliminated, "未知")
                        
                        self.wx.SendMsg(f"🚫 {eliminated} 被淘汰出局",who=self.sub_group)
                        
                        # 检查游戏是否结束
                        remaining_words = [self.words[p] for p in self.players]
                        if len(set(remaining_words)) == 1:  # 所有剩余玩家词汇相同
                            self.wx.SendMsg(f"🎉 卧底被找出！平民获胜！",who=self.sub_group)
                            self.game_active = False
                            break
                        else:
                            self.wx.SendMsg(f"😱 淘汰的是平民！游戏继续...",who=self.sub_group)
                    else:
                        self.wx.SendMsg("⚠️ 平票！本轮无人淘汰",who=self.sub_group)
                else:
                    self.wx.SendMsg("⚠️ 无人投票！本轮无人淘汰",who=self.sub_group)
                
                round_num += 1
                time.sleep(5)
            
            if self.game_active:
                self.wx.SendMsg("🎮 游戏结束！卧底获胜！",who=self.sub_group)
                    # 计算积分变动
                score_changes = {}
                for player in self.original_players:
                    if self.roles[player] == "卧底":
                        # 卧底获胜 +2分
                        # self.player_scores[player] = self.player_scores.get(player, 0) + 2
                        self.update_score(player, 2)
                        score_changes[player] = "+2"
                    else:
                        # 平民失败不加分
                        score_changes[player] = "+0"
                
                # 发送积分变动信息
                score_msg = "🏆 积分变动（卧底阵营胜利）：\n"
                for player, change in score_changes.items():
                    role = self.roles[player]
                    score_msg += f"{player}（{role}）: {change}分\n"
                self.wx.SendMsg(score_msg, who=self.sub_group)
                self.game_active = False
            else:  # 平民获胜
                self.wx.SendMsg("🎉 卧底被找出！平民获胜！")
                
                # 计算积分变动
                score_changes = {}
                for player in self.original_players:
                    if self.roles[player] == "平民":
                        # 平民获胜 +1分
                        # self.player_scores[player] = self.player_scores.get(player, 0) + 1
                        self.update_score(player, 1)
                        score_changes[player] = "+1"
                    else:
                        # 卧底失败不加分
                        score_changes[player] = "+0"
                
                # 发送积分变动信息
                score_msg = "🏆 积分变动（平民阵营胜利）：\n"
                for player, change in score_changes.items():
                    role = self.roles[player]
                    score_msg += f"{player}（{role}）: {change}分\n"
                self.wx.SendMsg(score_msg, group)
            # 保存积分到文件
            self.save_scores()
            # 显示当前积分榜
            self.show_scoreboard(group)
            
            self.game_active = False
        except Exception as e:
            print(f"游戏运行出错: {e}")
            self.wx.SendMsg("游戏出现错误，已终止",who=self.sub_group)
            self.game_active = False
        self.wx.SendMsg("🎮 再玩一局请发送：再来一局",who=self.sub_group)
        
     # 在修改积分的地方添加保存
    def update_score(self, player, points):
        """更新玩家积分并保存"""
        self.player_scores[player] = self.player_scores.get(player, 0) + points
        self.save_scores()
    # 添加显示积分榜的方法
    def show_scoreboard(self, group):   
        """显示当前积分榜"""
        if not self.player_scores:
            self.wx.SendMsg("暂无积分数据", group)
            return
        
        # 按积分排序
        sorted_scores = sorted(self.player_scores.items(), key=lambda x: x[1], reverse=True)
        
        score_msg = "🏆 当前积分榜：\n"
        for i, (player, score) in enumerate(sorted_scores, 1):
            score_msg += f"{i}. {player}: {score}分\n"
        
        self.wx.SendMsg(score_msg, who=group)
    def process_vote(self, voter, message):
        """处理数字投票"""
        try:
            parts = message.split()
            if len(parts) >= 2 and parts[0] == "投":
                try:
                    # 尝试解析投票数字
                    vote_num = int(parts[1])
                    
                    # 查找对应玩家
                    player_list = list(enumerate(self.players, start=1))
                    for num, player in player_list:
                        if num == vote_num:
                            # 记录投票 (voter: (vote_num, player))
                            self.votes[voter] = (vote_num, player)
                            
                            # 私信确认投票
                            # self.wx.SendMsg(f"✅ 你已投票给：{player} (编号 {vote_num})",who=voter)
                            return
                    
                    # 如果找不到对应玩家
                    self.wx.SendMsg(f"❌ 无效的玩家编号: {vote_num}",who=voter)
                    
                except ValueError:
                    # 如果无法解析为数字
                    self.wx.SendMsg("❌ 请使用数字投票，例如：投票 1", who=voter)
        except Exception as e:
            print(f"处理投票时出错: {e}")
    def manage_lobby(self, group, sender, command):
        """管理准备大厅"""
        # 确保大厅存在
        if group not in self.lobby_queues:
            self.lobby_queues[group] = []
            self.lobby_status[group] = time.time()
        
        # 更新大厅活跃时间
        self.lobby_status[group] = time.time()
        
        # 处理准备/取消准备命令
        if command == "准备":
            if sender not in self.lobby_queues[group]:
                self.lobby_queues[group].append(sender)
                self.wx.SendMsg(f"✅ {sender} 已准备！当前准备人数: {len(self.lobby_queues[group])}/{self.TeamMax}", who=group)
            else:
                self.wx.SendMsg(f"⚠️ {sender} 你已经准备过了！", who=group)
        elif command == "取消准备":
            if sender in self.lobby_queues[group]:
                self.lobby_queues[group].remove(sender)
                self.wx.SendMsg(f"❌ {sender} 已取消准备！当前准备人数: {len(self.lobby_queues[group])}/{self.TeamMax}", who=group)
            else:
                self.wx.SendMsg(f"⚠️ {sender} 你还没有准备！", who=group)
        
        # 显示准备列表
        if self.lobby_queues[group]:
            player_list = "\n".join([f"{i+1}. {player}" for i, player in enumerate(self.lobby_queues[group])])
            self.wx.SendMsg(f"📋 准备列表：\n{player_list}", who=group)
        else:
            self.wx.SendMsg("准备大厅已清空", who=group)
        
        # 检查是否满员
        if len(self.lobby_queues[group]) >= 4:
            self.start_game_from_lobby(group)
    
    def start_game_from_lobby(self, lobby_group):
        """从准备大厅开始游戏"""
        players = self.lobby_queues[lobby_group][:4]  # 取前8名玩家
        
        # 创建游戏群
        self.create_group(lobby_group, players)
        game_group=self.sub_group
        if not game_group:
            print("创建游戏群失败，请稍后再试")
            # self.wx.SendMsg("创建游戏群失败，请稍后再试", lobby_group)
            return
        
        # 通知玩家
        self.wx.SendMsg(f"🎉 准备完成！已创建游戏群: {game_group}", game_group)
        self.wx.SendMsg(f"请进入游戏群: {game_group} 开始游戏", game_group)
        
        # 清空准备队列
        self.lobby_queues[lobby_group] = self.lobby_queues[lobby_group][8:]
        
        # 如果还有剩余玩家
        if self.lobby_queues[lobby_group]:
            self.wx.SendMsg(f"剩余准备玩家: {len(self.lobby_queues[lobby_group])}/8", lobby_group)
            player_list = "\n".join([f"{i+1}. {player}" for i, player in enumerate(self.lobby_queues[lobby_group])])
            self.wx.SendMsg(f"📋 准备列表：\n{player_list}", lobby_group)
        
        # 在新群中开始游戏
        time.sleep(5)  # 给玩家时间加入新群
        self.start_game(game_group)
    def show_help(self, who):
        print(f"show_help: {who}")
        help_msg = """
🤖 微信机器人帮助：
1. 创建群聊 - 自动创建随机群聊
2. 谁是卧底 - 在群内开始文字版游戏
3. 积分榜 - 查看当前积分排名
4. 退出游戏 - 在游戏进行中退出
5. 帮助 - 显示此帮助信息

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
            elif msg.content == "积分榜":
                self.show_scoreboard(chatname)
            elif msg.content == "停止":
                self.wx.RemoveListenChat(self.official)
                self.wx.RemoveListenChat(self.current_group)
                self.wx.RemoveListenChat(self.sub_group)
                exit
    def run(self):
        """运行主监听循环"""
        # 循环添加监听对象
        self.selfnickname =  self.wx.GetMyInfo()['nickname']
        self.wx.SendMsg("机器人开始运行",who=self.current_group)
        self.wx.AddListenChat(nickname=self.official,callback=self.on_msg)
        self.wx.AddListenChat(nickname=self.current_group,callback=self.on_main_group_msg)
        self.wx.KeepRunning()


if __name__ == "__main__":
    bot = WeChatBot()
    bot.run()