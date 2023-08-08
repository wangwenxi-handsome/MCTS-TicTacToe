import math
import copy
import random


class Board:
    def __init__(self, s):
        self.s = s
    
    def step(self, x, y, value):
        if self.s[x][y] != '0':
            return False
        self.s[x][y] = value
        return True

    # 棋盘可视化
    def render(self, ):
        print("board now is:")
        for i in self.s:
            for j in i:
                print(j, end="")
            print()

    @staticmethod
    def done_util(char1, char2, char3):
        if char1 == char2 and char1 == char3 and char1 != '0':
            return 2 if char1 == 'o' else 3
        return 0

    # 游戏未结束返回0, 平局返回1, 'o'胜返回2, '*'胜返回3
    def done(self, ):
        tag = 0
        # 检查斜线
        tag = tag or self.done_util(self.s[0][0], self.s[1][1], self.s[2][2])
        tag = tag or self.done_util(self.s[0][2], self.s[1][1], self.s[2][0])
        for i in range(3):
            # 检查横行
            tag = tag or self.done_util(self.s[i][0], self.s[i][1], self.s[i][2])
            # 检查竖行
            tag = tag or self.done_util(self.s[0][i], self.s[1][i], self.s[2][i])
        # 检查是否棋盘还有空间下棋
        empty = False
        for i in self.s:
            for j in i:
                empty = empty or j == '0'
        # 棋盘满且没有检测到赢家则返回平局
        if (not empty) and (tag == 0):
            return 1
        return tag
    
    def get_empty_pos(self, ):
        empty_poses = []
        for i in range(len(self.s)):
            for j in range(len(self.s[i])):
                if self.s[i][j] == '0':
                    empty_poses.append((i, j))
        return empty_poses


class TreeNode:
    def __init__(self, board, father, pos_from_father):
        self.board = board
        self.child = []
        self.father = father
        self.value = 0
        self.times = 0
        self.pos_from_father = pos_from_father

    # value记录的是'*'胜利的次数，而轮到'o'落子时需要计算'o'胜利的次数
    def uct_score(self, iter, piece, c=2):
        if self.times == 0:
            return float("inf")
        if piece == '*':
            return self.value / self.times + c * math.sqrt(math.log(iter) / self.times)
        else:
            return 1 - self.value / self.times + c * math.sqrt(math.log(iter) / self.times)
        
    def expand(self, piece):
        empty_poses = self.board.get_empty_pos()
        for pos in empty_poses:
            new_board = copy.deepcopy(self.board)
            new_board.step(pos[0], pos[1], piece)
            self.child.append(TreeNode(new_board, self, pos))
    
    def select(self, iter, piece):
        max_uct_score = self.child[0].uct_score(iter, piece)
        select_node = self.child[0]
        for i in range(1, len(self.child)):
            child_uct_score = self.child[i].uct_score(iter, piece)
            if child_uct_score > max_uct_score:
                max_uct_score = child_uct_score
                select_node = self.child[i]
        return select_node
    
    def rollout(self, piece):
        rollout_board = copy.deepcopy(self.board)
        while(1):
            value = self.convert_done2value(rollout_board.done())
            if value is not None:
                return value
            random_pos = random.choice(rollout_board.get_empty_pos())
            rollout_board.step(random_pos[0], random_pos[1], piece)
            piece = 'o' if piece == '*' else '*'

    def update(self, value):
        self.value += value
        self.times += 1

    def is_leaf_node(self, ):
        return len(self.child) == 0
    
    def is_done(self, ):
        return self.board.done() > 0
    
    @staticmethod
    def convert_done2value(done_tag):
        if done_tag == 0:
            return None
        elif done_tag == 1:
            return 0
        elif done_tag == 2:
            return -1
        elif done_tag == 3:
            return 1

class MCTS:
    def __init__(self, board, max_iter=1000):
        self.root = TreeNode(copy.deepcopy(board), None, None)
        self.max_iter = max_iter

    def run(self, ):
        for i in range(self.max_iter):
            # 第一步先出'*'
            piece = '*'
            now = self.root
            # select
            while(not now.is_leaf_node()):
                now = now.select(i, piece)
                piece = 'o' if piece == '*' else '*'
            # expand
            value = TreeNode.convert_done2value(now.board.done())
            if value is None:
                now.expand(piece)
                # rollout
                now = now.select(i, piece)
                piece = 'o' if piece == '*' else '*'
                value = now.rollout(piece)
            # backup
            while(now.father != None):
                now.update(value)
                now = now.father
            now.update(value)

    def opt_step(self, ):
        max_times = 0
        opt_pos = None
        for i in self.root.child:
            if i.times > max_times:
                max_times = i.times
                opt_pos = i.pos_from_father
        return opt_pos[0], opt_pos[1]
