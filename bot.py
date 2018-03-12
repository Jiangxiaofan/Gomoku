import json
import random
BOARD_SIZE = 15

# 解析读入的JSON
full_input = json.loads(input())
if "data" in full_input:
    my_data = full_input["data"]; # 该对局中，上回合该Bot运行时存储的信息
else:
    my_data = None

# 分析自己收到的输入和自己过往的输出，并恢复状态
all_requests = full_input["requests"]
all_responses = full_input["responses"]
board = [[0 for x in range(BOARD_SIZE)] for y in range(BOARD_SIZE)]
raw = json.loads(all_requests[0])
if raw['x'] == raw['y'] == -1:
    val = 1
else:
    val = 2
for i in range(len(all_responses)):
    myInput = json.loads(all_requests[i]) # i回合我的输入
    myOutput = json.loads(all_responses[i]) # i回合我的输出
    # TODO: 根据规则，处理这些输入输出，从而逐渐恢复状态到当前回合
    if not myInput['x'] == myInput['y'] == -1:
        board[myInput['x']][myInput['y']] = 3 - val
    board[myOutput['x']][myOutput['y']] = val

# 看看自己最新一回合输入
curr_input = json.loads(all_requests[-1])
x = curr_input['x']
y = curr_input['y']
if x != -1 and y != -1:
    board[x][y] = 3 - val

# TODO: 作出决策并输出
all_moves = []
for x in range(BOARD_SIZE):
    for y in range(BOARD_SIZE):
        if board[x][y] == 0:
            all_moves.append((x, y))
x, y = random.choice(all_moves)
my_action = { "x": x, "y": y }

print(json.dumps({
    "response": my_action,
    "data": my_data # 可以存储一些前述的信息，在该对局下回合中使用，可以是dict或者字符串
}))
