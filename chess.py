# -*-utf-8-*-


import wx
import time
import copy

# 定义全局变量

glb_board_size = 0  # 棋盘大小
glb_board = []  # 棋盘
glb_cancel_board = []   # 用于悔棋
glb_color = 0   # 玩家颜色
glb_difficulty = 0
glb_weight = []


# 棋盘初始化
def board_setup():
    global glb_board_size
    global glb_board
    global glb_cancel_board

    board = []
    rolls = [0]
    for column in range(glb_board_size-1):  # 生成棋盘的每一行
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
    if glb_board[y][x] == 0:    # 如果这里可以下子
        for c in [[-1, -1], [0, -1], [1, -1], [-1, 0], [1, 0], [-1, 1], [0, 1], [1, 1]]:    # 八个方向依次判断
            x_dir = c[0]    # 每次判断需要增加的坐标
            y_dir = c[1]    # 每次判断需要增加的坐标
            xa = x  # 每次判断的坐标
            ya = y  # 每次判断的坐标
            finished = -1   # 没有结束
            turned = -1   # 可能不能翻子
            one_dir_turn_allowed = 0    # 每个方向可以翻的子
            while finished == -1:   # 如果没有结束
                if -1 < xa + x_dir < glb_board_size and -1 < ya + y_dir < glb_board_size:  # 如果没有超出边界
                    xa += x_dir  # 刷新每次判断的坐标
                    ya += y_dir  # 刷新每次判断的坐标
                    if glb_board[ya][xa] == color * -1:
                        turned = 1  # 可能可以翻子
                        one_dir_turn_allowed += 1   # 可以翻子的数量加1
                    elif glb_board[ya][xa] == color and turned == 1:    # 此方向可能可以翻子
                        turn_allowed += one_dir_turn_allowed    # 此方向可以翻的子的数量与其它方向的加总
                        xa = x  # 每次判断的坐标
                        ya = y  # 每次判断的坐标
                        while one_dir_turn_allowed > 0:  # 此方向可以翻子
                            xa += x_dir  # 刷新每次判断的坐标
                            ya += y_dir  # 刷新每次判断的坐标
                            place_to_turn.append([xa, ya])  # 写出可以翻的子的坐标
                            one_dir_turn_allowed -= 1
                        finished = 1    # 结束
                    else:   # 不能翻子或已经翻完棋子
                        finished = 1    # 结束
                else:   # 超出边界
                    finished = 1    # 结束

    turn_allowed *= glb_weight[y][x]    # 加权重

    return [turn_allowed, place_to_turn]


# 将需要翻转颜色的棋子进行反转
def color_turning(place_to_turn, color):
    for a in place_to_turn:
        glb_board[a[1]][a[0]] = color


def game_over():
    global glb_board
    global glb_board_size

    board = []
    rolls = [0]
    for column in range(glb_board_size-1):  # 生成棋盘的每一行
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
                equal_b = -1    # 还是可以下的
            if not turn_allowed_w[m][n] == 0:
                equal_w = -1    # 还是可以下的

    # 判断游戏状态
    if equal_b == 1 and equal_w == 1:   # 确实都不能下了
        # 判断黑子白子那个多
        result = 0
        for i in glb_board:
            for j in i:
                result += j
        if result == 0:   # 和棋
            return 2
        elif result > 0:    # 黑胜
            return 1
        elif result < 0:    # 百盛
            return -1
    else:
        return 0    # 还能下


# 生成选择颜色，初始化棋盘，选难度的对话框
class GameSetup(wx.Dialog):
    def __init__(self, parent):
        super(GameSetup, self).__init__(parent, title='新的游戏', size=(240, 350))
        panel = wx.Panel(self)

        radiobox_color = ['黑色', '白色']
        self.choose_color = wx.RadioBox(panel, -1, '选择你的颜色', pos=(45, 10), choices=radiobox_color,
                                        style=wx.RA_SPECIFY_COLS)
        self.choose_color.Bind(wx.EVT_RADIOBOX, self.ChooseColor)

        radiobox_size = ['6 * 6', '8 * 8', '10 * 10']
        self.choose_color = wx.RadioBox(panel, -1, '选择棋盘大小', pos=(10, 80), choices=radiobox_size,
                                        style=wx.RA_SPECIFY_COLS)
        self.choose_color.Bind(wx.EVT_RADIOBOX, self.ChooseSize)
        # 设定初始值，按序号进行选择，序号从0开始计数
        self.choose_color.SetSelection(1)

        radiobox_difficulty = ['简单', '困难']
        self.choose_color = wx.RadioBox(panel, -1, '选择AI难度', pos=(40, 150), choices=radiobox_difficulty,
                                        style=wx.RA_SPECIFY_COLS)
        self.choose_color.Bind(wx.EVT_RADIOBOX, self.ChooseDifficulty)

        txt = '点击确定开始游戏'
        wx.StaticText(panel, wx.ID_ANY, txt, (35, 220))

        self.click_done = wx.Button(panel, -1, label='确定', size=(75, 25), pos=(75, 270))  # 按钮基本参数设置
        self.Bind(wx.EVT_BUTTON, self.OnClickOk, self.click_done)  # 按下时触发 如果玩家选黑

        self.Center()
        self.Show()

    def ChooseColor(self, event):
        global glb_color

        # 获取选中项
        if event.GetInt() == 0:
            glb_color = 1
        elif event.GetInt() == 1:
            glb_color = -1

    def ChooseSize(self, event):
        global glb_board_size

        # 获取选中项
        if event.GetInt() == 0:
            glb_board_size = 6
        elif event.GetInt() == 1:
            glb_board_size = 8
        elif event.GetInt() == 2:
            glb_board_size = 10

    def ChooseDifficulty(self, event):
        global glb_difficulty

        # 获取选中项
        if event.GetInt() == 0:
            glb_difficulty = 1
        elif event.GetInt() == 1:
            glb_difficulty = 2

    def OnClickOk(self, e):
        global glb_difficulty
        global glb_board_size
        global glb_color

        if glb_color == 0:
            glb_color = 1
        if glb_board_size == 0:
            glb_board_size = 8
        if glb_difficulty == 0:
            glb_difficulty = 1

        self.Destroy()


# 生成用户界面
class Chess(wx.Frame):
    def __init__(self, parent, title):
        super(Chess, self).__init__(parent, title=title, size=(760, 800))

        self.InitUI()
        self.Centre()
        self.Show()

    def InitUI(self):
        global glb_board
        global glb_board_size

        glb_board_size = 10
        board_setup()

        menuBar = wx.MenuBar()
        fileMenu = wx.Menu()  # 菜单栏 文件
        helpMenu = wx.Menu()  # 菜单栏 帮助

        new_game = fileMenu.Append(wx.ID_ANY, '&新游戏')  # 菜单栏 文件 新游戏
        step_back = fileMenu.Append(wx.ID_CANCEL, '&悔棋')  # 菜单栏 文件 悔棋
        fileMenu.AppendSeparator()  # 菜单栏 文件 分割线
        Quit = fileMenu.Append(wx.ID_EXIT, '&退出')  # 菜单栏 文件 退出

        Help = helpMenu.Append(wx.ID_HELP, '&帮助')
        About = helpMenu.Append(wx.ID_ABOUT, '关于')

        menuBar.Append(fileMenu, '&文件')
        menuBar.Append(helpMenu, '&帮助')
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU, self.OnStepBack, step_back)
        self.Bind(wx.EVT_MENU, self.OnNewGame, new_game)
        self.Bind(wx.EVT_MENU, self.OnQuit, Quit)

        self.Bind(wx.EVT_MENU, self.OnHelp, Help)
        self.Bind(wx.EVT_MENU, self.OnAbout, About)

        panel = wx.Panel(self)
        box = wx.BoxSizer(wx.HORIZONTAL)
        fgs = wx.FlexGridSizer(10, 10, -2, -2)

        button_blank = wx.Image("button_blank.bmp", wx.BITMAP_TYPE_BMP).ConvertToBitmap()
        button_black = wx.Image("button_black.bmp", wx.BITMAP_TYPE_BMP).ConvertToBitmap()
        button_white = wx.Image("button_white.bmp", wx.BITMAP_TYPE_BMP).ConvertToBitmap()

        self.button = []
        rolls = [0]
        for column in range(glb_board_size - 1):  # 生成棋盘的每一行
            rolls.append(0)
        for roll in range(glb_board_size):  # 生成棋盘的每一列
            self.button.append(copy.deepcopy(rolls))  # 简单的append语句会使每一行的存储地址为同一个，所以需使用深copy
        for m in range(0, glb_board_size):
            for n in range(0, glb_board_size):
                if glb_board[m][n] == 0:
                    self.button[m][n] = wx.BitmapButton(panel, -1, button_blank)
                    fgs.Add(self.button[m][n], 1, flag=wx.EXPAND)
                    self.Bind(wx.EVT_BUTTON, lambda evt, x=m, y=n: self.OnClick(evt, x, y), self.button[m][n])
                elif glb_board[m][n] == 1:
                    self.button[m][n] = wx.BitmapButton(panel, -1, button_black)
                    fgs.Add(self.button[m][n], 1, flag=wx.EXPAND)
                    self.Bind(wx.EVT_BUTTON, lambda evt, x=m, y=n: self.OnClick(evt, x, y), self.button[m][n])
                elif glb_board[m][n] == -1:
                    self.button[m][n] = wx.BitmapButton(panel, -1, button_white)
                    fgs.Add(self.button[m][n], 1, flag=wx.EXPAND)
                    self.Bind(wx.EVT_BUTTON, lambda evt, x=m, y=n: self.OnClick(evt, x, y), self.button[m][n])

        box.Add(fgs, proportion=1, flag=wx.ALL | wx.EXPAND, border=15)
        panel.SetSizer(box)

    def computer_move(self, color):
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
            wx.MessageDialog(None, txt, '电脑无法下子', wx.OK).ShowModal()    # 告诉玩家这个事实
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

        # 设置按钮图像
        button_black = wx.Image("button_black.bmp", wx.BITMAP_TYPE_BMP).ConvertToBitmap()
        button_white = wx.Image("button_white.bmp", wx.BITMAP_TYPE_BMP).ConvertToBitmap()
        button_blank = wx.Image("button_blank.bmp", wx.BITMAP_TYPE_BMP).ConvertToBitmap()
        # 让按钮闪烁（提示玩家）
        if color == 1:
            for a in range(2):
                self.button[y][x].SetBitmap(button_black)
                self.button[y][x].Update()
                time.sleep(0.25)
                self.button[y][x].SetBitmap(button_blank)
                self.button[y][x].Update()
                time.sleep(0.25)
        elif color == -1:
            for a in range(2):
                self.button[y][x].SetBitmap(button_white)
                self.button[y][x].Update()
                time.sleep(0.25)
                self.button[y][x].SetBitmap(button_blank)
                self.button[y][x].Update()
                time.sleep(0.25)

        # 初始化/刷新所有按钮
        for m in range(glb_board_size):
            for n in range(glb_board_size):
                if glb_board[m][n] == 1:
                    self.button[m][n].SetBitmap(button_black)
                elif glb_board[m][n] == -1:
                    self.button[m][n].SetBitmap(button_white)

    def human_move(self, color, y, x):
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

            # 设置按钮图像
            button_black = wx.Image("button_black.bmp", wx.BITMAP_TYPE_BMP).ConvertToBitmap()
            button_white = wx.Image("button_white.bmp", wx.BITMAP_TYPE_BMP).ConvertToBitmap()
            button_blank = wx.Image("button_blank.bmp", wx.BITMAP_TYPE_BMP).ConvertToBitmap()
            # 让按钮闪烁（提示玩家）
            if color == 1:
                for a in range(2):
                    self.button[y][x].SetBitmap(button_black)
                    self.button[y][x].Update()
                    time.sleep(0.25)
                    self.button[y][x].SetBitmap(button_blank)
                    self.button[y][x].Update()
                    time.sleep(0.25)
            elif color == -1:
                for a in range(2):
                    self.button[y][x].SetBitmap(button_white)
                    self.button[y][x].Update()
                    time.sleep(0.25)
                    self.button[y][x].SetBitmap(button_blank)
                    self.button[y][x].Update()
                    time.sleep(0.25)

            # 初始化/刷新所有按钮
            for m in range(glb_board_size):
                for n in range(glb_board_size):
                    if glb_board[m][n] == 1:
                        self.button[m][n].SetBitmap(button_black)
                        self.button[m][n].Update()
                    elif glb_board[m][n] == -1:
                        self.button[m][n].SetBitmap(button_white)
                        self.button[m][n].Update()
            return 0    # 下子成功
        else:   # 否则（这个位置不能下子）
            txt = '这个位置不能下子，请你换一个位置下子。'
            wx.MessageDialog(None, txt, 'Error', wx.ICON_ERROR).ShowModal()  # 提示玩家
            return -1   # 下子失败

    # 玩家按下cancel
    def OnStepBack(self, e):
        global glb_cancel_board
        global glb_board

        # 把棋盘变成上一步的样子
        for a in range(glb_board_size):
            for b in range(glb_board_size):
                glb_board[a][b] = glb_cancel_board[a][b]

        # 初始化/刷新所有按钮
        button_black = wx.Image("button_black.bmp", wx.BITMAP_TYPE_BMP).ConvertToBitmap()
        button_white = wx.Image("button_white.bmp", wx.BITMAP_TYPE_BMP).ConvertToBitmap()
        button_blank = wx.Image("button_blank.bmp", wx.BITMAP_TYPE_BMP).ConvertToBitmap()
        for m in range(glb_board_size):
            for n in range(glb_board_size):
                if glb_board[m][n] == 1:
                    self.button[m][n].SetBitmap(button_black)
                elif glb_board[m][n] == -1:
                    self.button[m][n].SetBitmap(button_white)
                elif glb_board[m][n] == 0:
                    self.button[m][n].SetBitmap(button_blank)

    # 玩家按下restart
    def OnNewGame(self, e):
        global glb_color
        global glb_board
        global glb_board_size
        global glb_cancel_board
        global glb_difficulty

        # 选颜色，初始化棋盘，选难度
        glb_board_size = 0
        glb_difficulty = 0
        glb_color = 0
        GameSetup(self).ShowModal()

        if glb_difficulty == 0 or glb_color == 0 or glb_board_size == 0:
            txt = '请点击 文件 里的 新游戏 来开始一盘新的游戏。'
            wx.MessageDialog(None, txt, 'Error', wx.ICON_ERROR).ShowModal()
        else:
            board_setup()
            weight_setup()

            button_black = wx.Image("button_black.bmp", wx.BITMAP_TYPE_BMP).ConvertToBitmap()
            button_white = wx.Image("button_white.bmp", wx.BITMAP_TYPE_BMP).ConvertToBitmap()
            button_blank = wx.Image("button_blank.bmp", wx.BITMAP_TYPE_BMP).ConvertToBitmap()
            # 初始化/刷新所有按钮
            for m in range(glb_board_size):
                for n in range(glb_board_size):
                    if glb_board[m][n] == 1:
                        self.button[m][n].SetBitmap(button_black)
                    elif glb_board[m][n] == -1:
                        self.button[m][n].SetBitmap(button_white)
                    elif glb_board[m][n] == 0:
                        self.button[m][n].SetBitmap(button_blank)

            button_gray = wx.Image("button_gray.bmp", wx.BITMAP_TYPE_BMP).ConvertToBitmap()
            if glb_board_size == 6:
                c = []
                for a in range(6):
                    for b in range(4):
                        c.append(a)
                M = [6, 7, 8, 9] * 6 + c + [6, 7, 8, 9, 6, 7, 8, 9, 6, 7, 8, 9, 6, 7, 8, 9]
                N = c + [6, 7, 8, 9] * 6 + [6, 6, 6, 6, 7, 7, 7, 7, 8, 8, 8, 8, 9, 9, 9, 9]
                for a in range(len(M)):
                    self.button[M[a]][N[a]].SetBitmap(button_gray)
            elif glb_board_size == 8:
                c = []
                for a in range(8):
                    for b in range(2):
                        c.append(a)
                M = [8, 9] * 8 + c + [8, 9, 8, 9]
                N = c + [8, 9] * 8 + [8, 8, 9, 9]
                for a in range(len(M)):
                    self.button[M[a]][N[a]].SetBitmap(button_gray)

            for a in range(10):
                for b in range(10):
                    self.button[a][b].Update()

            if glb_color == -1:  # 如果玩家选白，则电脑先下，否则等待玩家按下按钮
                glb_color = 1
                self.computer_move(glb_color)
                glb_color = -1

    # 玩家按下quit
    def OnQuit(self, e):
        txt = '你确定要退出程序吗？'
        quit_check = wx.MessageDialog(None, txt, '退出', wx.YES_NO | wx.NO_DEFAULT)  # 生成提示对话框
        if quit_check.ShowModal() == wx.ID_YES:    # 如果玩家确认
            self.Close()    # 关闭用户界面

    def OnHelp(self, e):
        txt = '暂无帮助'
        diag_help = wx.MessageDialog(None, txt, '帮助', wx.OK)  # 生成提示对话框
        diag_help.ShowModal()

    def OnAbout(self, e):
        txt = 'Chess 1.0\n\nW.Workshop 出品\n版本：1.0\n\n\nCopyright © 2020-2025 W.Workshop'
        diag_about = wx.MessageDialog(None, txt, '关于', wx.OK)  # 生成提示对话框
        diag_about.ShowModal()

    # 玩家按下棋子，x、y为玩家按下的棋子的纵横坐标
    def OnClick(self, e, x, y):
        global glb_board
        global glb_color
        if glb_difficulty == 0 or glb_color == 0 or glb_board_size == 0:
            txt = '请点击 文件 里的 新游戏 来开始一盘新的游戏'
            wx.MessageDialog(None, txt, 'Error', wx.ICON_ERROR).ShowModal()
        else:
            try:
                human = self.human_move(glb_color, x, y)    # 玩家走棋判断
                game = game_over()  # 游戏状态判断
                if human == 0 and game == 0:    # human==0时即为玩家走棋成功，game==0时即为游戏未结束
                    time.sleep(1)
                    glb_color *= -1  # 变为电脑的颜色
                    self.computer_move(glb_color)   # 电脑走棋
                    game = game_over()  # 游戏状态判断
                    glb_color *= -1  # 变回玩家颜色

                if game == 2:   # 和棋
                    txt = '和棋'
                    wx.MessageDialog(None, txt, '和棋', wx.OK).ShowModal()  # 提示消息框
                elif game == 1:   # 黑胜
                    txt = '黑棋胜！'
                    wx.MessageDialog(None, txt, '黑棋胜！', wx.OK).ShowModal()  # 提示消息框
                elif game == -1:   # 白胜
                    txt = '白棋胜！'
                    wx.MessageDialog(None, txt, '白棋胜！', wx.OK).ShowModal()  # 提示消息框
            except IndexError:
                txt = '这个位置不能下子，请你换一个位置下子。'
                wx.MessageDialog(None, txt, 'Error', wx.ICON_ERROR).ShowModal()  # 提示玩家
                return


# 主程序
if __name__ == '__main__':
    app = wx.App()
    Chess(None, title='Chess')
    app.MainLoop()
