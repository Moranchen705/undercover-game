"""
游戏策略模块
负责生成描述、投票决策等游戏策略逻辑
"""
from typing import List, Optional, Dict


class GameStrategy:
    """游戏策略类"""
    
    def __init__(self):
        self.my_word = None  # 自己的词语
        self.my_role = None  # 自己的身份：'civilian' 或 'undercover'
        self.descriptions_history = []  # 历史描述记录
        self.vote_history = []  # 历史投票记录
        self.eliminated_groups = []  # 已淘汰的组
    
    def set_word(self, word: str, role: str):
        """
        设置自己的词语和身份
        :param word: 词语
        :param role: 身份（'civilian' 或 'undercover'）
        """
        self.my_word = word
        self.my_role = role
    
    def generate_description(self, word: str) -> str:
        """
        根据词语生成描述
        :param word: 词语
        :return: 描述文本
        """
        # TODO: 实现描述生成策略
        # 策略建议：
        # 1. 如果是平民：生成贴合词语的描述，但要避免直接说出词语
        # 2. 如果是卧底：生成模糊的描述，避免暴露身份
        
        # 示例：简单策略（需要根据实际需求改进）
        if self.my_role == 'civilian':
            # 平民策略：生成贴合词语的描述
            return f"这是一个关于{word}的描述"
        else:
            # 卧底策略：生成模糊的描述
            return "这是一个常见的物品"
    
    def decide_vote(self, active_groups: List[str], descriptions: Dict[str, str]) -> Optional[str]:
        """
        决定投票给谁
        :param active_groups: 存活组列表
        :param descriptions: 当前回合的描述 {组名: 描述}
        :return: 要投票的组名，如果无法决定返回None
        """
        # TODO: 实现投票决策策略
        # 策略建议：
        # 1. 如果是平民：找出描述最可疑的组（可能是卧底）
        # 2. 如果是卧底：投票给最可能被怀疑的平民，转移注意力
        
        # 示例：简单策略（需要根据实际需求改进）
        if not active_groups:
            return None
        
        # 简单策略：随机选择一个（实际应该根据描述内容分析）
        import random
        candidates = [g for g in active_groups if g not in self.eliminated_groups]
        if candidates:
            return random.choice(candidates)
        return None
    
    def update_descriptions(self, descriptions: Dict[str, str]):
        """
        更新描述历史
        :param descriptions: 当前回合的描述
        """
        self.descriptions_history.append(descriptions)
    
    def update_vote_history(self, voter: str, target: str):
        """
        更新投票历史
        :param voter: 投票者
        :param target: 被投票者
        """
        self.vote_history.append({'voter': voter, 'target': target})
    
    def update_eliminated(self, eliminated: List[str]):
        """
        更新已淘汰组列表
        :param eliminated: 已淘汰的组
        """
        self.eliminated_groups.extend(eliminated)


# 测试代码
if __name__ == '__main__':
    strategy = GameStrategy()
    strategy.set_word("苹果", "civilian")
    
    desc = strategy.generate_description("苹果")
    print(f"生成的描述: {desc}")
    
    vote = strategy.decide_vote(["组1", "组2", "组3"], {})
    print(f"投票决策: {vote}")

