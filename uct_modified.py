# online uct_search
import json
from math import sqrt
import random
import time
BOARD_SIZE = 15
C = 5
board = [[0 for x in range(BOARD_SIZE)] for y in range(BOARD_SIZE)]
episodes = 0

        
class Node(object):
    def __init__(self, action=None, parent=None, prior=None):
        self.action = action
        self.parent = parent
        self.children = []
        self.Q = 0
        self.visits = 0
        self.p = prior

    def tree_policy(self):
        return max(self.children,
                   key=lambda x: x.Q + C*x.p*sqrt(self.visits/(x.visits+1)))

    def most_visit_child(self):
        return max(self.children, key=lambda x: x.visits)

    def update(self, reward):
        self.visits += 1
        self.Q += (reward - self.Q) / self.visits

def adjacent(grid, x, y, stone):
    if grid[x][y] != 0:
        return False
    if x - 1 >= 0 and grid[x-1][y] != 0:
        return True
    if y - 1 >= 0 and grid[x][y-1] != 0:
        return True
    if x + 1 < 15 and grid[x+1][y] != 0:
        return True
    if y + 1 < 15 and grid[x][y+1] != 0:
        return True
    if x + 1 < 15 and y + 1 < 15 and grid[x+1][y+1] != 0:
        return True
    if x + 1 < 15 and y - 1 >= 0 and grid[x+1][y-1] != 0:
        return True
    if x - 1 >= 0 and y + 1 < 15 and grid[x-1][y+1] != 0:
        return True
    if x - 1 >= 0 and y - 1 >= 0 and grid[x-1][y-1] != 0:
        return True
    return False
    
def get_all_moves(grid, stone):
    all_moves = []
    for x in range(15):
        for y in range(15):
            if adjacent(grid, x, y, stone):
                all_moves.append((x, y))
    if len(all_moves) == 0:
        return [(x, y) for x in range(5, 11) for y in range(5, 11)]
    return all_moves

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

def loop(root, stone, x, y):
    grid = [board[_][:] for _ in range(15)]
    leaf_stone = stone
    # selection
    while terminal_state(grid, x, y) == 0 and len(root.children) != 0:
        root = root.tree_policy()
        x, y = root.action
        grid[x][y] = stone
        stone = 3 - stone
        
    # expansion
    if terminal_state(grid, x, y) == 0:
        leaf_stone = stone
        all_moves = get_all_moves(grid, stone)
        for move in all_moves:
            child = Node(move, root, 1.0/len(all_moves))
            root.children.append(child)

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
        root.update(-reward)
        reward = -reward
        root = root.parent

def uct_search(stone, x, y):
    global episodes
    st = time.time()
    root = Node()
    while time.time() - st < 2:
        loop(root, stone, x, y)
        episodes += 1
    return root.most_visit_child().action

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
