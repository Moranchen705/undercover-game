"""
游戏方客户端主程序
使用Tkinter实现GUI界面
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
from api_client import APIClient
from game_strategy import GameStrategy


class GameClient:
    """游戏客户端主类"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("谁是卧底 - 游戏方客户端")
        self.root.geometry("800x600")
        
        # 初始化
        self.api_client = None
        self.strategy = GameStrategy()
        self.group_name = ""
        self.my_word = ""
        self.my_role = None
        self.is_running = False
        self.status_polling_thread = None
        self.countdown_thread = None
        self.countdown_seconds = 0
        self.countdown_running = False
        self.current_round = 0
        self.all_descriptions = []  # 存储所有组的描述
        
        # 创建界面
        self.create_widgets()
    
    def create_widgets(self):
        """创建GUI组件"""
        # 顶部：服务器配置区域
        config_frame = ttk.LabelFrame(self.root, text="服务器配置", padding=10)
        config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(config_frame, text="服务器地址:").grid(row=0, column=0, padx=5)
        self.server_url_entry = ttk.Entry(config_frame, width=30)
        self.server_url_entry.insert(0, "http://127.0.0.1:5000")
        self.server_url_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(config_frame, text="组名:").grid(row=0, column=2, padx=5)
        self.group_name_entry = ttk.Entry(config_frame, width=20)
        self.group_name_entry.grid(row=0, column=3, padx=5)
        
        self.register_btn = ttk.Button(config_frame, text="注册", command=self.register_group)
        self.register_btn.grid(row=0, column=4, padx=5)
        
        # 中间：游戏信息区域
        info_frame = ttk.LabelFrame(self.root, text="游戏信息", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 左侧：词语和状态
        left_frame = ttk.Frame(info_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        ttk.Label(left_frame, text="我的词语:", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        self.word_label = ttk.Label(left_frame, text="未获取", font=("Arial", 16), foreground="blue")
        self.word_label.pack(anchor=tk.W, pady=5)
        
        ttk.Label(left_frame, text="当前状态:", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(10, 0))
        self.status_label = ttk.Label(left_frame, text="等待注册", font=("Arial", 12))
        self.status_label.pack(anchor=tk.W)
        
        ttk.Label(left_frame, text="当前回合:", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(10, 0))
        self.round_label = ttk.Label(left_frame, text="0", font=("Arial", 12))
        self.round_label.pack(anchor=tk.W)
        
        # 右侧：描述和日志区域
        right_frame = ttk.Frame(info_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        # 其他组描述区域
        desc_frame = ttk.LabelFrame(right_frame, text="所有组描述", padding=5)
        desc_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        self.descriptions_text = scrolledtext.ScrolledText(desc_frame, height=8, width=40)
        self.descriptions_text.pack(fill=tk.BOTH, expand=True)
        
        # 游戏日志区域
        ttk.Label(right_frame, text="游戏日志:", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        self.log_text = scrolledtext.ScrolledText(right_frame, height=7, width=40)
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 底部：操作区域
        action_frame = ttk.LabelFrame(self.root, text="游戏操作", padding=10)
        action_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 描述区域
        desc_frame = ttk.Frame(action_frame)
        desc_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(desc_frame, text="描述:").pack(side=tk.LEFT, padx=5)
        self.description_entry = ttk.Entry(desc_frame, width=40)
        self.description_entry.pack(side=tk.LEFT, padx=5)
        
        self.desc_time_label = ttk.Label(desc_frame, text="剩余时间: --", foreground="red")
        self.desc_time_label.pack(side=tk.LEFT, padx=5)
        
        self.submit_desc_btn = ttk.Button(desc_frame, text="提交描述", command=self.submit_description)
        self.submit_desc_btn.pack(side=tk.LEFT, padx=5)
        
        # 投票区域
        vote_frame = ttk.Frame(action_frame)
        vote_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(vote_frame, text="投票给:").pack(side=tk.LEFT, padx=5)
        self.vote_target_var = tk.StringVar()
        self.vote_target_combo = ttk.Combobox(vote_frame, textvariable=self.vote_target_var, width=20)
        self.vote_target_combo.pack(side=tk.LEFT, padx=5)
        
        self.submit_vote_btn = ttk.Button(vote_frame, text="提交投票", command=self.submit_vote)
        self.submit_vote_btn.pack(side=tk.LEFT, padx=5)
        
        # 初始状态：禁用操作按钮
        self.submit_desc_btn.config(state=tk.DISABLED)
        self.submit_vote_btn.config(state=tk.DISABLED)
    
    def log(self, message: str):
        """添加日志"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
    
    def register_group(self):
        """注册组名"""
        server_url = self.server_url_entry.get().strip()
        group_name = self.group_name_entry.get().strip()
        
        if not server_url or not group_name:
            messagebox.showerror("错误", "请输入服务器地址和组名")
            return
        
        # 初始化API客户端
        self.api_client = APIClient(server_url)
        self.group_name = group_name
        
        # 尝试注册
        self.log(f"正在注册组名: {group_name}")
        result = self.api_client.register(group_name)
        
        if result:
            self.log(f"注册成功！总组数: {result.get('total_groups', 0)}")
            self.register_btn.config(state=tk.DISABLED)
            self.server_url_entry.config(state=tk.DISABLED)
            self.group_name_entry.config(state=tk.DISABLED)
            
            # 开始状态轮询
            self.start_status_polling()
        else:
            self.log("注册失败，请检查服务器地址和组名")
            messagebox.showerror("错误", "注册失败，请检查服务器地址和组名")
    
    def start_status_polling(self):
        """开始状态轮询"""
        if self.is_running:
            return
        
        self.is_running = True
        
        def poll_status():
            while self.is_running:
                try:
                    status = self.api_client.get_status()
                    if status:
                        self.root.after(0, self.update_status, status)
                    time.sleep(2)  # 每2秒轮询一次
                except Exception as e:
                    self.log(f"状态轮询错误: {e}")
                    time.sleep(2)
        
        self.status_polling_thread = threading.Thread(target=poll_status, daemon=True)
        self.status_polling_thread.start()
        self.log("开始状态轮询...")
    
    def update_status(self, status_data: dict):
        """更新游戏状态显示"""
        status = status_data.get('status', '')
        round_num = status_data.get('round', 0)
        active_groups = status_data.get('active_groups', [])
        describe_order = status_data.get('describe_order', [])
        eliminated_groups = status_data.get('eliminated_groups', [])
        
        # 保存状态数据，供其他方法使用
        self.last_status_data = status_data
        
        # 更新状态显示
        status_map = {
            'waiting': '等待注册',
            'registered': '已注册',
            'word_assigned': '词语已分配',
            'describing': '描述阶段',
            'voting': '投票阶段',
            'round_end': '回合结束',
            'game_end': '游戏结束'
        }
        self.status_label.config(text=status_map.get(status, status))
        self.round_label.config(text=str(round_num))
        
        # 如果词语已分配，获取词语
        if status == 'word_assigned' and not self.my_word:
            word = self.api_client.get_word(self.group_name)
            if word:
                self.my_word = word
                self.word_label.config(text=word)
                self.log(f"获取到词语: {word}")
                # 判断身份（需要根据实际情况调整）
                # 这里简化处理，实际应该根据词语判断
        
        # 根据状态启用/禁用按钮
        if status == 'describing':
            # 描述阶段：启用描述提交按钮，禁用投票按钮
            # 如果已经超时，描述按钮保持禁用状态
            if not (self.countdown_seconds == 0 and not self.countdown_running):
                self.submit_desc_btn.config(state=tk.NORMAL)
            else:
                # 已超时，禁用描述按钮
                self.submit_desc_btn.config(state=tk.DISABLED)
            self.submit_vote_btn.config(state=tk.DISABLED)
            # 启动描述时间倒计时（3秒限制）
            if round_num != self.current_round:  # 新回合开始
                self.current_round = round_num
                self.start_description_countdown()
                self.log(f"第 {round_num} 回合开始，请在3秒内提交描述！")
        elif status == 'voting':
            # 投票阶段：禁用描述提交，启用投票按钮
            # 无论描述是否超时，投票功能都应该可用
            self.submit_desc_btn.config(state=tk.DISABLED)
            self.submit_vote_btn.config(state=tk.NORMAL)
            # 停止倒计时
            self.stop_countdown()
            
            # 更新投票目标列表
            # 优先使用 active_groups，如果为空则使用 describe_order
            if not active_groups:
                if describe_order:
                    # 从 describe_order 获取，排除已淘汰的组
                    active_groups = [g for g in describe_order if g not in eliminated_groups]
                    self.log(f"从 describe_order 获取 active_groups: {active_groups}")
                else:
                    # 如果 describe_order 也为空，记录警告
                    self.log(f"⚠️ active_groups 和 describe_order 都为空")
            
            # 如果 active_groups 仍然为空，尝试从所有注册的组获取（备用方案）
            if not active_groups:
                # 尝试通过 API 获取所有组
                all_groups = self.api_client.get_groups()
                if all_groups:
                    active_groups = [g['name'] for g in all_groups if g['name'] not in eliminated_groups]
                    self.log(f"从 get_groups API 获取 active_groups: {active_groups}")
            
            # 过滤出可以投票的组（排除自己和已淘汰的组）
            other_groups = [g for g in active_groups if g != self.group_name and g not in eliminated_groups]
            
            # 调试日志（只在第一次或列表变化时记录，避免日志过多）
            if not hasattr(self, '_last_vote_groups') or self._last_vote_groups != other_groups:
                self.log(f"投票阶段 - active_groups: {active_groups}, describe_order: {describe_order}, other_groups: {other_groups}")
                self._last_vote_groups = other_groups
            
            if other_groups:
                self.vote_target_combo['values'] = other_groups
                # 如果当前值不在列表中，设置默认值
                current_value = self.vote_target_var.get()
                if not current_value or current_value not in other_groups:
                    self.vote_target_var.set(other_groups[0])
            else:
                # 如果没有其他组，记录详细日志（只记录一次，避免日志过多）
                if not hasattr(self, '_vote_empty_logged') or not self._vote_empty_logged:
                    self.log(f"⚠️ 投票目标列表为空！")
                    self.log(f"  - active_groups: {active_groups}")
                    self.log(f"  - describe_order: {describe_order}")
                    self.log(f"  - eliminated_groups: {eliminated_groups}")
                    self.log(f"  - 我的组名: {self.group_name}")
                    self._vote_empty_logged = True
                self.vote_target_combo['values'] = []
                self.vote_target_var.set("")
            
            # 获取并显示所有组的描述
            self.update_all_descriptions()
        else:
            self.submit_desc_btn.config(state=tk.DISABLED)
            self.submit_vote_btn.config(state=tk.DISABLED)
            self.stop_countdown()
    
    def start_description_countdown(self):
        """启动描述倒计时（3秒）"""
        self.stop_countdown()  # 先停止之前的倒计时
        self.countdown_seconds = 3
        self.countdown_running = True
        
        def countdown():
            while self.countdown_seconds > 0 and self.countdown_running:
                self.root.after(0, self.update_countdown_label, self.countdown_seconds)
                time.sleep(1)
                self.countdown_seconds -= 1
            
            if self.countdown_seconds == 0 and self.countdown_running:
                self.root.after(0, self.countdown_timeout)
        
        self.countdown_thread = threading.Thread(target=countdown, daemon=True)
        self.countdown_thread.start()
    
    def stop_countdown(self):
        """停止倒计时"""
        self.countdown_running = False
        self.countdown_seconds = 0
        self.root.after(0, self.update_countdown_label, 0)
    
    def update_countdown_label(self, seconds):
        """更新倒计时标签"""
        if seconds > 0:
            self.desc_time_label.config(text=f"剩余时间: {seconds}秒", foreground="red")
        else:
            self.desc_time_label.config(text="剩余时间: --", foreground="gray")
    
    def countdown_timeout(self):
        """倒计时超时处理"""
        self.desc_time_label.config(text="剩余时间: 已超时", foreground="red")
        self.submit_desc_btn.config(state=tk.DISABLED)
        # 只禁用描述提交，不影响投票功能
        self.log(f"⚠️ {self.group_name}组描述超时（3秒限制），无法提交描述")
        # 不显示弹窗，只在日志中提示，避免打断用户
    
    def update_all_descriptions(self):
        """更新所有组的描述显示，包括超时的组"""
        descriptions = self.api_client.get_descriptions()
        status = self.api_client.get_status()
        
        if descriptions:
            self.all_descriptions = descriptions.get('descriptions', [])
            self.descriptions_text.delete(1.0, tk.END)
            
            round_num = descriptions.get('round', 0)
            describe_order = []
            
            # 获取描述顺序
            if status:
                describe_order = status.get('describe_order', [])
            
            if self.all_descriptions or describe_order:
                self.descriptions_text.insert(tk.END, f"第 {round_num} 回合描述：\n\n")
                
                # 获取已提交描述的组名
                submitted_groups = {desc.get('group') for desc in self.all_descriptions}
                
                # 按顺序显示所有组的描述状态
                for group_name in describe_order:
                    if group_name in submitted_groups:
                        # 找到对应的描述
                        desc = next((d for d in self.all_descriptions if d.get('group') == group_name), None)
                        if desc:
                            desc_text = desc.get('description', '')
                            desc_time = desc.get('time', '')
                            # 格式化时间
                            try:
                                from datetime import datetime
                                dt = datetime.fromisoformat(desc_time.replace('Z', '+00:00'))
                                time_str = dt.strftime('%H:%M:%S')
                            except:
                                time_str = desc_time
                            self.descriptions_text.insert(tk.END, f"[{group_name}] {desc_text} ({time_str})\n")
                    else:
                        # 未提交描述，显示超时（红色）
                        self.descriptions_text.insert(tk.END, f"[{group_name}] 描述超时\n")
                        # 标记超时文本
                        start_pos = self.descriptions_text.index("end-1l linestart")
                        end_pos = self.descriptions_text.index("end-1l lineend")
                        self.descriptions_text.tag_add("timeout", start_pos, end_pos)
                        self.descriptions_text.tag_config("timeout", foreground="red")
            elif self.all_descriptions:
                # 如果没有顺序信息，只显示已提交的描述
                self.descriptions_text.insert(tk.END, f"第 {round_num} 回合描述：\n\n")
                for desc in self.all_descriptions:
                    group_name = desc.get('group', '未知')
                    desc_text = desc.get('description', '')
                    desc_time = desc.get('time', '')
                    # 格式化时间
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(desc_time.replace('Z', '+00:00'))
                        time_str = dt.strftime('%H:%M:%S')
                    except:
                        time_str = desc_time
                    self.descriptions_text.insert(tk.END, f"[{group_name}] {desc_text} ({time_str})\n")
            else:
                self.descriptions_text.insert(tk.END, "暂无描述")
    
    def submit_description(self):
        """提交描述"""
        description = self.description_entry.get().strip()
        if not description:
            messagebox.showerror("错误", "请输入描述")
            return
        
        # 检查是否超时
        if self.countdown_seconds == 0 and not self.countdown_running:
            self.log(f"⚠️ {self.group_name}组描述超时，无法提交")
            messagebox.showerror("错误", "描述提交时间已过（3秒限制），无法提交")
            return
        
        self.log(f"提交描述: {description}")
        result = self.api_client.submit_description(self.group_name, description)
        
        if result:
            self.log(f"描述提交成功！回合: {result.get('round', 0)}")
            self.description_entry.delete(0, tk.END)
            self.submit_desc_btn.config(state=tk.DISABLED)
            self.stop_countdown()
            # 更新描述显示
            self.update_all_descriptions()
        else:
            self.log("描述提交失败")
            messagebox.showerror("错误", "描述提交失败")
    
    def submit_vote(self):
        """提交投票"""
        target = self.vote_target_var.get().strip()
        if not target:
            messagebox.showerror("错误", "请选择投票目标")
            return
        
        # 检查是否投给自己
        if target == self.group_name:
            messagebox.showerror("错误", "不能投票给自己")
            return
        
        self.log(f"投票给: {target}")
        # 获取当前状态，确保在投票阶段
        status = self.api_client.get_status()
        if status and status.get('status') != 'voting':
            self.log(f"⚠️ 当前状态不是投票阶段: {status.get('status')}")
            messagebox.showerror("错误", f"当前状态不是投票阶段，无法投票")
            return
        
        result = self.api_client.submit_vote(self.group_name, target)
        
        # 注意：成功时服务器返回空字典 {}，需要用 is not None 判断
        if result is not None:
            self.log("投票提交成功！")
            self.submit_vote_btn.config(state=tk.DISABLED)
        else:
            # 获取详细的错误信息
            error_msg = self.api_client.last_error or "投票提交失败"
            self.log(f"投票提交失败: {error_msg}")
            self.log(f"  - 我的组名: {self.group_name}")
            self.log(f"  - 目标组: {target}")
            self.log(f"  - 当前状态: {status.get('status') if status else '未知'}")
            messagebox.showerror("错误", f"投票提交失败\n\n{error_msg}")


def main():
    """主函数"""
    root = tk.Tk()
    app = GameClient(root)
    root.mainloop()


if __name__ == '__main__':
    main()

