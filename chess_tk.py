# -*-utf-8-*-

import tkinter as tk
import tkinter.messagebox
from tkinter import Menu
import time
import copy

# 定义全局变量
glb_board_size = 10  # 棋盘大小
glb_board = []  # 棋盘
glb_cancel_board = []  # 用于悔棋
glb_color = 0  # 玩家颜色
glb_difficulty = 0  # 电脑难度
glb_weight = []  # 用于 难
glb_button_image = [] # 用于更换按钮颜色

#button_black = tk.PhotoImage
#button_blank = tk.PhotoImage
#button_white = tk.PhotoImage
#button_gray = tk.PhotoImage


# 棋盘初始化
def board_setup():
    global glb_board_size
    global glb_board
    global glb_cancel_board

    board = []
    rolls = [0]
    for column in range(glb_board_size - 1):  # 生成棋盘的每一行
        rolls.append(0)
    for roll in range(glb_board_size):  # 生成棋盘的每一列
        board.append(copy.deepcopy(rolls))  # 简单的append语句会使每一行的存储地址为同一个，所以需使用深copy
    glb_board = copy.deepcopy(board)
    glb_cancel_board = copy.deepcopy(board)

    # 生成初始棋盘中间的4个棋子
    chess_pieces = int(glb_board_size / 2)
    glb_board[chess_pieces - 1][chess_pieces - 1] = 1
    glb_board[chess_pieces][chess_pieces] = 1
    glb_board[chess_pieces - 1][chess_pieces] = -1
    glb_board[chess_pieces][chess_pieces - 1] = -1


# 权重初始化
def weight_setup():
    global glb_weight
    global glb_board_size

    glb_weight = []
    rolls = [2]
    for column in range(glb_board_size - 1):  # 生成棋盘的每一行
        rolls.append(2)
    for roll in range(glb_board_size):  # 生成棋盘的每一列
        glb_weight.append(copy.deepcopy(rolls))  # 简单的append语句会使每一行的存储地址为同一个，所以需使用深copy

    if glb_difficulty == 2:
        # 把一部分地方认为是没用的
        cheap_position = []
        for a in range(1, glb_board_size - 1):
            cheap_position.append([1, a])
            cheap_position.append([a, 1])
            cheap_position.append([copy.copy(glb_board_size - 2), a])
            cheap_position.append([a, copy.copy(glb_board_size - 2)])
        for a in cheap_position:
            glb_weight[a[0]][a[1]] = 1

        # 把一部分地方认为是非常有用的
        expensive_position = []
        for a in range(0, glb_board_size):
            expensive_position.append([0, a])
            expensive_position.append([a, 0])
            expensive_position.append([copy.copy(glb_board_size - 1), a])
            expensive_position.append([a, copy.copy(glb_board_size - 1)])
        for a in expensive_position:
            glb_weight[a[0]][a[1]] += 8


# 翻子判断，也可用于判断是否可以下在这里
def turn_check(color, x, y):
    global glb_board
    global glb_board_size
    global glb_weight

    turn_allowed = 0
    place_to_turn = []
    if glb_board[y][x] == 0:  # 如果这里可以下子
        for c in [[-1, -1], [0, -1], [1, -1], [-1, 0], [1, 0], [-1, 1], [0, 1], [1, 1]]:  # 八个方向依次判断
            x_dir = c[0]  # 每次判断需要增加的坐标
            y_dir = c[1]  # 每次判断需要增加的坐标
            xa = x  # 每次判断的坐标
            ya = y  # 每次判断的坐标
            finished = -1  # 没有结束
            turned = -1  # 可能不能翻子
            one_dir_turn_allowed = 0  # 每个方向可以翻的子
            while finished == -1:  # 如果没有结束
                if -1 < xa + x_dir < glb_board_size and -1 < ya + y_dir < glb_board_size:  # 如果没有超出边界
                    xa += x_dir  # 刷新每次判断的坐标
                    ya += y_dir  # 刷新每次判断的坐标
                    if glb_board[ya][xa] == color * -1:
                        turned = 1  # 可能可以翻子
                        one_dir_turn_allowed += 1  # 可以翻子的数量加1
                    elif glb_board[ya][xa] == color and turned == 1:  # 此方向可能可以翻子
                        turn_allowed += one_dir_turn_allowed  # 此方向可以翻的子的数量与其它方向的加总
                        xa = x  # 每次判断的坐标
                        ya = y  # 每次判断的坐标
                        while one_dir_turn_allowed > 0:  # 此方向可以翻子
                            xa += x_dir  # 刷新每次判断的坐标
                            ya += y_dir  # 刷新每次判断的坐标
                            place_to_turn.append([xa, ya])  # 写出可以翻的子的坐标
                            one_dir_turn_allowed -= 1
                        finished = 1  # 结束
                    else:  # 不能翻子或已经翻完棋子
                        finished = 1  # 结束
                else:  # 超出边界
                    finished = 1  # 结束

    turn_allowed *= glb_weight[y][x]  # 加权重

    return [turn_allowed, place_to_turn]


# 将需要翻转颜色的棋子进行反转
def color_turning(place_to_turn, color):
    for a in place_to_turn:
        glb_board[a[1]][a[0]] = color


# 判断游戏书否结束
def game_over():
    global glb_board
    global glb_board_size

    board = []
    rolls = [0]
    for column in range(glb_board_size - 1):  # 生成棋盘的每一行
        rolls.append(0)
    for roll in range(glb_board_size):  # 生成棋盘的每一列
        board.append(copy.deepcopy(rolls))  # 简单的append语句会使每一行的存储地址为同一个，所以需使用深copy
    turn_allowed_b = copy.deepcopy(board)
    turn_allowed_w = copy.deepcopy(board)

    # 黑棋与白棋每个地方可以翻的子
    for a in range(glb_board_size):
        for b in range(glb_board_size):
            turn_allowed_b[b][a] = turn_check(1, a, b)[0]
            turn_allowed_w[b][a] = turn_check(-1, a, b)[0]

    # 判断黑白两方是否都无棋可下
    equal_b = 1  # 假设都不能下了
    equal_w = 1  # 假设都不能下了
    for m in range(glb_board_size):
        for n in range(glb_board_size):
            if not turn_allowed_b[m][n] == 0:
                equal_b = -1  # 还是可以下的
            if not turn_allowed_w[m][n] == 0:
                equal_w = -1  # 还是可以下的

    # 判断游戏状态
    if equal_b == 1 and equal_w == 1:  # 确实都不能下了
        # 判断黑子白子那个多
        result = 0
        for i in glb_board:
            for j in i:
                result += j
        if result == 0:  # 和棋
            return 2
        elif result > 0:  # 黑胜
            return 1
        elif result < 0:  # 百盛
            return -1
    else:
        return 0  # 还能下


root = tk.Tk()
root.title('chess')
root.geometry('700x700')


def computer_move(color):
    global glb_board
    global glb_board_size
    global glb_difficulty

    # 判断棋盘每个位置可否下子及可翻子数量
    turn_allowed = []
    rolls = []
    for column in range(glb_board_size):  # 生成棋盘的每一行
        rolls.append(0)
    for roll in range(glb_board_size):  # 生成棋盘的每一列
        turn_allowed.append(copy.deepcopy(rolls))  # 简单的append语句会使每一行的存储地址为同一个，所以需使用深copy

    for roll in range(glb_board_size):
        for column in range(glb_board_size):
            turn_allowed[column][roll] = turn_check(color, roll, column)[0]

    # 判断电脑是不是还可以下子
    equal = 1
    for m in range(glb_board_size):
        for n in range(glb_board_size):
            if not turn_allowed[m][n] < 1:
                equal = -1
    if equal == 1:  # 电脑不能下子
        txt = '电脑没有办法进行这一回合,\n现在是你的回合。'
        tk.messagebox.showinfo(title='电脑无法下子', message=txt)    # 告诉玩家这个事实
        return  # 退出，让玩家继续下

    # 判断权重最高的地方
    lis2 = []
    lis3 = []
    for c in turn_allowed:
        lis3.append(c.index(max(c)))
        lis2.append(max(c))
    y = lis2.index(max(lis2))
    x = lis3[y]

    color_turning(turn_check(color, x, y)[1], color)    # 翻转需要翻转颜色的棋子
    glb_board[y][x] = color

    # 让按钮闪烁（提示玩家）
    if color == 1:
        for a in range(2):
            glb_button_image[y][x]['image'] = button_black
            root.update()
            time.sleep(0.25)
            glb_button_image[y][x]['image'] = button_blank
            root.update()
            time.sleep(0.25)
    elif color == -1:
        for a in range(2):
            glb_button_image[y][x]['image'] = button_white
            root.update()
            time.sleep(0.25)
            glb_button_image[y][x]['image'] = button_blank
            root.update()
            time.sleep(0.25)

    # 初始化/刷新所有按钮
    for m in range(glb_board_size):
        for n in range(glb_board_size):
            if glb_board[m][n] == 1:
                glb_button_image[m][n]['image'] = button_black
            elif glb_board[m][n] == -1:
                glb_button_image[m][n]['image'] = button_white
    root.update()


def human_move(color, y, x):
    global glb_board
    global glb_cancel_board
    global glb_board_size

    if glb_board[y][x] == 0 and turn_check(color, x, y)[0] > 0 and not color == 0:  # 如果这个位置可以下子
        # 刷新glb_cancel_board
        for a in range(glb_board_size):
            for b in range(glb_board_size):
                glb_cancel_board[a][b] = glb_board[a][b]

        color_turning(turn_check(color, x, y)[1], color)    # 翻转需要翻转颜色的棋子
        glb_board[y][x] = color

        # 让按钮闪烁（提示玩家）
        if color == 1:
            for a in range(2):
                glb_button_image[y][x]['image'] = button_black
                root.update()
                time.sleep(0.25)
                glb_button_image[y][x]['image'] = button_blank
                root.update()
                time.sleep(0.25)
        elif color == -1:
            for a in range(2):
                glb_button_image[y][x]['image'] = button_white
                root.update()
                time.sleep(0.25)
                glb_button_image[y][x]['image'] = button_blank
                root.update()
                time.sleep(0.25)

        # 初始化/刷新所有按钮
        for m in range(glb_board_size):
            for n in range(glb_board_size):
                if glb_board[m][n] == 1:
                    glb_button_image[m][n]['image'] = button_black
                elif glb_board[m][n] == -1:
                    glb_button_image[m][n]['image'] = button_white
        root.update()

        return 0    # 下子成功

    else:   # 否则（这个位置不能下子）
        txt = '这个位置不能下子，请你换一个位置下子。'
        tk.messagebox.showerror(title='Error', message=txt)  # 提示玩家
        return -1   # 下子失败


def OnClick(x, y):
    global glb_board
    global glb_color
    if glb_difficulty == 0 or glb_color == 0 or glb_board_size == 0:
        txt = '请点击 文件 里的 新游戏 来开始一盘新的游戏'
        tk.messagebox.showerror(title='Error', message=txt)
    else:
        try:
            human = human_move(glb_color, x, y)    # 玩家走棋判断
            game = game_over()  # 游戏状态判断
            if human == 0 and game == 0:    # human==0时即为玩家走棋成功，game==0时即为游戏未结束
                time.sleep(1)
                glb_color *= -1  # 变为电脑的颜色
                computer_move(glb_color)   # 电脑走棋
                game = game_over()  # 游戏状态判断
                glb_color *= -1  # 变回玩家颜色

            if game == 2:   # 和棋
                txt = '和棋'
                tk.messagebox.showerror(title='Error', message=txt)  # 提示消息框
            elif game == 1:   # 黑胜
                txt = '黑棋胜！'
                tk.messagebox.showerror(title='Error', message=txt)  # 提示消息框
            elif game == -1:   # 白胜
                txt = '白棋胜！'
                tk.messagebox.showerror(title='Error', message=txt)  # 提示消息框
        except IndexError:
            txt = '这个位置不能下子，请你换一个位置下子。'
            tk.messagebox.showerror(title='Error', message=txt)  # 提示玩家
            return


def OnNewGame():
    # 设置基本信息
    newgame = tk.Toplevel()
    newgame.title('新游戏')
    newgame.geometry('250x200')

    def OnDone():
        global glb_color
        global glb_board
        global glb_board_size
        global glb_cancel_board
        global glb_difficulty

        # 获取颜色难度棋盘大小
        glb_color = var_color.get()
        glb_board_size = var_boardsize.get()
        glb_difficulty = var_difficulty.get()

        # 设置颜色难度棋盘大小
        if glb_difficulty == 0 or glb_color == 0 or glb_board_size == 0:
            txt = '请点击 文件 里的 新游戏 来开始一盘新的游戏。'
            tk.messagebox.showerror(title='Error', message=txt)
        else:
            # 初始化棋盘权重
            board_setup()
            weight_setup()

            # 初始化所有按钮
            for m in range(glb_board_size):
                for n in range(glb_board_size):
                    if glb_board[m][n] == 1:
                        glb_button_image[m][n]['image'] = button_black
                    elif glb_board[m][n] == -1:
                        glb_button_image[m][n]['image'] = button_white
                    elif glb_board[m][n] == 0:
                        glb_button_image[m][n]['image'] = button_blank

            # 初始化灰色按钮
            if glb_board_size == 6:
                c = []
                for a in range(6):
                    for b in range(4):
                        c.append(a)
                M = [6, 7, 8, 9] * 6 + c + [6, 7, 8, 9, 6, 7, 8, 9, 6, 7, 8, 9, 6, 7, 8, 9]
                N = c + [6, 7, 8, 9] * 6 + [6, 6, 6, 6, 7, 7, 7, 7, 8, 8, 8, 8, 9, 9, 9, 9]
                for a in range(len(M)):
                    glb_button_image[M[a]][N[a]]['image'] = button_gray
            elif glb_board_size == 8:
                c = []
                for a in range(8):
                    for b in range(2):
                        c.append(a)
                M = [8, 9] * 8 + c + [8, 9, 8, 9]
                N = c + [8, 9] * 8 + [8, 8, 9, 9]
                for a in range(len(M)):
                    glb_button_image[M[a]][N[a]]['image'] = button_gray

            # 刷新
            root.update()

            # 如果玩家选白，则电脑先下，否则等待玩家按下按钮





        # 关闭窗口
        newgame.quit()
        newgame.destroy()

    # 创建复选框及确定按钮
    tk.Label(newgame, text='你的颜色：').grid(row=0, column=0)
    var_color = tk.IntVar()
    tk.Radiobutton(newgame, text="执黑", variable=var_color, value=1).grid(row=1, column=0)
    tk.Radiobutton(newgame, text="执白", variable=var_color, value=-1).grid(row=1, column=2)

    tk.Label(newgame, text='棋盘大小：').grid(row=2, column=0)
    var_boardsize = tk.IntVar()
    tk.Radiobutton(newgame, text="6 x 6", variable=var_boardsize, value=6).grid(row=3, column=0)
    tk.Radiobutton(newgame, text="8 x 8", variable=var_boardsize, value=8).grid(row=3, column=1)
    tk.Radiobutton(newgame, text="10 x 10", variable=var_boardsize, value=10).grid(row=3, column=2)

    tk.Label(newgame, text='电脑难度：').grid(row=4, column=0)
    var_difficulty = tk.IntVar()
    tk.Radiobutton(newgame, text="简单", variable=var_difficulty, value=1).grid(row=5, column=0)
    tk.Radiobutton(newgame, text="困难", variable=var_difficulty, value=2).grid(row=5, column=2)

    tk.Label(newgame, text='点击确定开始游戏：').grid(row=6, column=1)
    tk.Button(newgame, text='确定', command=OnDone).grid(row=7, column=1)

    # 显示
    newgame.mainloop()


def OnExit():
    result = tk.messagebox.askyesno(title='退出', message='是否退出？')
    if result:
        root.quit()
        root.destroy()
        exit()


def OnAbout():
    txt = 'Chess 2.0\n\nW.Workshop 出品\n版本：2.0\n\n\nCopyright © 2020-2025 W.Workshop'
    tk.messagebox.showinfo(title='关于', message=txt)


def OnHelp():
    txt = '暂无帮助'
    tk.messagebox.showinfo(title='帮助', message=txt)


# 初始化棋盘
board_setup()
# 创建按钮列表
for i in range(10):
    glb_button_image.append([])
    for j in range(10):
        glb_button_image[i].append([])
# 打开按钮
button_black = tk.PhotoImage(file='button_black.gif')
button_blank = tk.PhotoImage(file='button_blank.gif')
button_white = tk.PhotoImage(file='button_white.gif')
button_gray = tk.PhotoImage(file='button_gray.gif')

# 创建按钮
for m in range(0, glb_board_size):
    for n in range(0, glb_board_size):
        if glb_board[m][n] == 0:
            glb_button_image[m][n] = tk.Button(root, image=button_blank, command=lambda x=m, y=n: OnClick(x, y))
        elif glb_board[m][n] == 1:
            glb_button_image[m][n] = tk.Button(root, image=button_black, command=lambda x=m, y=n: OnClick(x, y))
        elif glb_board[m][n] == -1:
            glb_button_image[m][n] = tk.Button(root, image=button_white, command=lambda x=m, y=n: OnClick(x, y))

for m in range(0, glb_board_size):
    for n in range(0, glb_board_size):
        glb_button_image[m][n].grid(row=m, column=n)

# 创建菜单栏功能
menuBar = Menu(root)
root.config(menu=menuBar)

# 创建菜单项
fileMenu = Menu(menuBar, tearoff=0)
menuBar.add_cascade(label='文件', menu=fileMenu)
helpMenu = Menu(menuBar, tearoff=0)
menuBar.add_cascade(label='帮助', menu=helpMenu)

# 添加选项
fileMenu.add_command(label='新游戏', command=OnNewGame)
fileMenu.add_command(label='悔棋', command=OnNewGame)
fileMenu.add_separator()
fileMenu.add_command(label='退出', command=OnExit)
helpMenu.add_command(label='帮助', command=OnHelp)
helpMenu.add_command(label='关于', command=OnAbout)

# 主循环
root.mainloop()
