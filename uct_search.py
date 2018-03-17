# online uct_search
import json
from math import sqrt, log
import random
import time
BOARD_SIZE = 15
board = [[0 for x in range(BOARD_SIZE)] for y in range(BOARD_SIZE)]
episodes = 0
df = 0.9

def board_full(grid):
    return all(grid[x][y] != 0 for x in range(BOARD_SIZE) for y in range(BOARD_SIZE))

def check_winner(grid, x, y):
    for direction in ((0,1),(1,-1),(1,0),(1,1)):
        cnt = 1
        for i in (-1, 1):
            for j in range(1, 5):
                row = x + i * j * direction[0]
                col = y + i * j * direction[1]
                if row < 0 or row > BOARD_SIZE - 1 or col < 0 or col > BOARD_SIZE - 1:
                    break
                if grid[row][col] == grid[x][y]:
                    cnt += 1
                else:
                    break
        if cnt >= 5:
            return True
    return False
    
def terminal_state(grid, x, y):
    if x < 0 and y < 0:
        return 0
    if check_winner(grid, x, y):
        return 2
    if board_full(grid):
        return 1
    return 0

class State(object):
    def __init__(self, ):
        self.player = 1
        self.board = [[0 for x in range(BOARD_SIZE)] for y in range(BOARD_SIZE)]
        return

    def do_move(x, y):
        self.board[x][y] = self.player
        self.player = 3 - self.player

    def check_winner(x, y):
        for direction in ((0,1),(1,-1),(1,0),(1,1)):
            cnt = 1
            for i in (-1, 1):
                for j in range(1, 5):
                    row = x + i * j * direction[0]
                    col = y + i * j * direction[1]
                    if row < 0 or row > BOARD_SIZE - 1 or col < 0 or col > BOARD_SIZE - 1:
                        break
                    if self.board[row][col] == self.board[x][y]:
                        cnt += 1
                    else:
                        break
            if cnt >= 5:
                return True
        return False
    
    def is_terminal(x, y):
        if self.check_winner(x, y):
            return self.player
        
class Node(object):
    def __init__(self, action=None, parent=None, actions=None):
        self.action = action
        self.parent = parent
        self.actions = actions
        self.children = []
        self.wins = 0
        self.visits = 0

    def ucb_child(self):
        return max(self.children,
                   key=lambda x: x.wins/x.visits + sqrt(2*log(self.visits-1)/x.visits))

    def highest_reward_child(self):
        return max(self.children, key=lambda x: x.wins/x.visits)
    def most_visit_child(self):
        return max(self.children, key=lambda x: x.visits)

    def update(self, reward):
        self.wins += reward
        self.visits += 1

def on_board(x, y):
    return 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE

def position_taken(grid, x, y):
    if on_board(x, y) and grid[x][y] != 0:
        return True
    return False

def adjacent(grid, x, y, stone):
    if grid[x][y] != 0:
        return False
    for i, j in ((0,1),(1,-1),(1,0),(1,1),
                 (0,-1),(-1,1),(-1,0),(-1,-1)):
        if position_taken(grid, x+i, y+j):
            return True
    return False
    
def get_all_moves(grid, stone):
    all_moves = []
    for x in range(15):
        for y in range(15):
            if adjacent(grid, x, y, stone):
                all_moves.append((x, y))
    if len(all_moves) == 0:
        return [(x, y) for x in range(7, 9) for y in range(7, 9)]
    return all_moves

def loop(root, stone, x, y):
    grid = [board[_][:] for _ in range(15)]
    leaf_stone = stone
    # selection
    while terminal_state(grid, x, y) == 0 and len(root.actions) == 0:
        root = root.ucb_child()
        x, y = root.action
        grid[x][y] = stone
        stone = 3 - stone
        
    # expansion
    if terminal_state(grid, x, y) == 0:
        x, y = random.choice(root.actions)
        grid[x][y] = stone
        leaf_stone = stone
        root.actions.remove((x, y))
        child = Node((x, y), root, get_all_moves(grid, stone))
        root.children.append(child)
        root = child
        stone = 3 - stone

    # simulation
    while terminal_state(grid, x, y) == 0:
        x, y = random.choice(get_all_moves(grid, stone))
        grid[x][y] = stone
        stone = 3 - stone
    
    # back up
    result = terminal_state(grid, x, y)
    if result == 1:
        reward = 0
    else:
        reward = 1 if stone != leaf_stone else -1
    while root:
        root.update(reward)
        reward = -df*reward
        root = root.parent

def uct_search(stone, x, y):
    global episodes
    end = time.time() + 3
    root = Node(actions=get_all_moves(board, stone))
    root.update(0)
    while time.time() < end:
        loop(root, stone, x, y)
        episodes += 1
    return root.highest_reward_child().action

def place_at(x, y, stone):
    if x >= 0 and y >= 0:
        board[x][y] = stone
        
if __name__ == "__main__":
    # 解析读入的JSON
    full_input = json.loads(input())
    if "data" in full_input:
        my_data = full_input["data"]; # 该对局中，上回合该Bot运行时存储的信息
    else:
        my_data = None

    # 分析自己收到的输入和自己过往的输出，并恢复状态
    all_requests = full_input["requests"]
    all_responses = full_input["responses"]
    if all_requests[0]['x'] == all_requests[0]['y'] == -1:
        stone = 1
    else:
        stone = 2

    for i in range(len(all_responses)):
        my_input = all_requests[i] # i回合我的输入
        my_output = all_responses[i] # i回合我的输出
        # TODO: 根据规则，处理这些输入输出，从而逐渐恢复状态到当前回合
        place_at(my_input['x'], my_input['y'], 3 - stone)
        place_at(my_output['x'], my_output['y'], stone)

    # 看看自己最新一回合输入
    curr_input = all_requests[-1]
    place_at(curr_input['x'], curr_input['y'], 3 - stone)

    # TODO: 作出决策并输出
    x, y = uct_search(stone, curr_input['x'], curr_input['y'])
    my_action = {'x': x, 'y': y}

    print(json.dumps({"response": my_action,
                      "data": episodes}))
