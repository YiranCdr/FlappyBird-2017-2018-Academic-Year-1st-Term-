# -*- coding: utf-8 -*-
import cocos
import time
from cocos.scene import *
from cocos.actions import *
from cocos.layer import *  
from cocos.text  import *
from cocos.menu import *
from pyglet import font
from pyglet.window import key
import random
import pipe
from atlas import *
from land import *
from bird import *
from score import *
from pipe import *
from collision import *
from network import *
import common

#vars
gameLayer = None
gameScene = None
spriteBird = None
land_1 = None
land_2 = None
startLayer = None
pipes = None
score = 0
listener = None
account = None
password = None
ipTextField = None
errorLabel = None
isGamseStart = False
# my vars
REGISTER = 1
LOG_IN = 2
GUEST = 3
state = 0
game_difficulty = 0 
start_time = None
end_time = None
total_time = None
championAccount = None
championScore = None
notice_send = None # 要广播的消息
#####################################################
# 重写VerticalMenuLayout
CENTER = font.Text.CENTER
LEFT = font.Text.LEFT
RIGHT = font.Text.RIGHT

# Vertical Align
TOP = font.Text.TOP
BOTTOM = font.Text.BOTTOM

def myVerticalMenuLayout(menu):
    width, height = director.get_window_size()
    fo = font.load(menu.font_item['font_name'], menu.font_item['font_size'])
    fo_height = int((fo.ascent - fo.descent) * 1.5)

    if menu.menu_halign == CENTER:
        pos_x = width // 2
    elif menu.menu_halign == RIGHT:
        pos_x = width - menu.menu_hmargin
    elif menu.menu_halign == LEFT:
        pos_x = menu.menu_hmargin
    else:
        raise Exception("Invalid anchor_x value for menu")

    for idx, i in enumerate(menu.children):
        item = i[1]
        if menu.menu_valign == CENTER:
            pos_y = (height + (len(menu.children) - 2 * idx) * fo_height - menu.title_height) * 0.5
        elif menu.menu_valign == TOP:
            pos_y = (height - ((idx + 0.8) * fo_height) - menu.title_height - menu.menu_vmargin)
        elif menu.menu_valign == BOTTOM:
            pos_y = (0 + fo_height * (len(menu.children) - idx) + menu.menu_vmargin)
        item.transform_anchor = (pos_x, pos_y)
        item.generateWidgets(pos_x, pos_y, menu.font_item, menu.font_item_selected)

# 重写EntryMenuItem
class myEntryMenuItem(MenuItem):

    value = property(lambda self: u''.join(self._value), lambda self, v: setattr(self, '_value', list(v)))

    def __init__(self, label, callback_func, value, max_length=0):

        self._value = list(value)
        self._label = label
        super(myEntryMenuItem, self).__init__("%s %s" % (label, value), callback_func)
        self.max_length = max_length

    def on_text(self, text):
        if self.max_length == 0 or len(self._value) < self.max_length:
            self._value.append(text)
            self._calculate_value()
        return True

    def on_key_press(self, symbol, modifiers):
        if symbol == key.BACKSPACE:
            try:
                self._value.pop()
            except IndexError:
                pass
            self._calculate_value()
            return True

    def _calculate_value(self):
        self.callback_func(self.value)
        new_text = u"%s %s" % (self._label, self.value)
        startChanging = False
        i = 0
        tmp_str = ''
        for char in new_text:
            if char == ' ':
                continue
            if char == ':':
                startChanging = True
                tmp_str += char
            elif startChanging:
                tmp_str += '*'
            else:
                tmp_str += char
            i += 1
        self.item.text = tmp_str
        self.item_selected.text = tmp_str
##################################################################

def initGameLayer():
    global spriteBird, gameLayer, land_1, land_2
    # gameLayer: 游戏场景所在的layer
    gameLayer = Layer()
    # add background
    bg = createAtlasSprite("bg_day")
    bg.position = (common.visibleSize["width"]/2, common.visibleSize["height"]/2)
    gameLayer.add(bg, z=0, name="bg")
    # add moving land
    land_1, land_2 = createLand()
    gameLayer.add(land_1, z=10, name="land_1")
    gameLayer.add(land_2, z=10, name="land_2")
    # add gameLayer to gameScene
    gameScene.add(gameLayer)

def game_start(_gameScene):
    global gameScene
    # 给gameScene赋值
    gameScene = _gameScene
    initGameLayer()
    connected = connect(gameScene)
    logIn_button = LogInMenu()
    gameLayer.add(logIn_button, z=20, name="logIn_button")

# 登录界面
class LogInMenu(Menu):
    def __init__(self):  
        super(LogInMenu, self).__init__()
        self.menu_valign = CENTER  
        self.menu_halign = CENTER
        items = [
                (ImageMenuItem(common.load_image("button_register.png"), self.register)),
                (ImageMenuItem(common.load_image("button_logIn.png"), self.logIn)),
                (ImageMenuItem(common.load_image("button_guest.png"), self.guest)),
                (ImageMenuItem(common.load_image("button_exit.png"), self.exit))
                ]  
        self.create_menu(items,selected_effect=zoom_in(),unselected_effect=zoom_out())

    def register(self):
        removeContent()
        connected = connect(gameScene)
        if not connected:
            content = "Cannot connect to server"
            showContent(content)
        else:
            global state
            state = REGISTER
            gameLayer.remove("logIn_button")
            input_button = InputMenu()
            gameLayer.add(input_button, z=20, name="input_button")

    def logIn(self):
        removeContent()
        connected = connect(gameScene)
        if not connected:
            content = "Cannot connect to server"
            showContent(content)
        else:
            global state
            state = LOG_IN
            gameLayer.remove("logIn_button")
            input_button = InputMenu()
            gameLayer.add(input_button, z=20, name="input_button")

    def guest(self):
        removeContent()
        global state
        state = GUEST
        gameLayer.remove("logIn_button")
        start_button = SingleGameStartMenu()
        gameLayer.add(start_button, z=20, name="start_button")

    def exit(self):
        gameScene.end()

# 用户名和密码输入，限长为8
class InputMenu(Menu):
    def __init__(self):
        # global account, password
        super(InputMenu, self).__init__()
        self.menu_valign = CENTER
        self.menu_halign = LEFT
        self.font_item['font_size'] = 20
        self.font_item_selected['font_size'] = 20
        items = [
                (EntryMenuItem('name:', self.getName, '', 8)),
                (myEntryMenuItem('pswd:', self.getPassword, '', 8)),
                (ImageMenuItem(common.load_image("button_ok.png"), self.checkInputAnd)),
                (ImageMenuItem(common.load_image("button_back.png"), self.back))
                ]
        self.create_menu(items,selected_effect=zoom_out(),unselected_effect=zoom_out(),layout_strategy=myVerticalMenuLayout)

    def getName(self, value):
        global account
        account = value

    def getPassword(self, value):
        global password
        password = value

    def checkInputAnd(self):
        send_log_in_message(state, account, password)

    def back(self):
        gameLayer.remove('input_button')
        logIn_button = LogInMenu()
        gameLayer.add(logIn_button, z=20, name="logIn_button")

class SingleGameStartMenu(Menu):
    def __init__(self):  
        super(SingleGameStartMenu, self).__init__()
        self.menu_valign = CENTER
        self.menu_halign = CENTER
        if state == GUEST:
            items = [
                    (ImageMenuItem(common.load_image("button_start.png"), self.gameStart)),
                    (ImageMenuItem(common.load_image("button_backToLogIn.png"), backToLogIn))
                    ] 
        else:
            items = [
                    (ImageMenuItem(common.load_image("button_start.png"), self.gameStart)),
                    (ImageMenuItem(common.load_image("button_broadcast.png"), self.enterNotice)),
                    (ImageMenuItem(common.load_image("button_logOut.png"), logOut))
                    ]  
        self.create_menu(items,selected_effect=zoom_in(),unselected_effect=zoom_out())

    def gameStart(self):
        gameLayer.remove("start_button")
        difficulty_button = DifficultyMenu()
        gameLayer.add(difficulty_button, z=20, name="difficulty_button")
        # singleGameReady() 

    def enterNotice(self):
        gameLayer.remove("start_button")
        notice_input_button = NoticeInputMenu()
        gameLayer.add(notice_input_button, z=20, name="notice_input_button")

# 向Server发送logOut消息
def logOut():
    global gameScene, gameLayer
    connected = connect(gameScene)  # connect is from network.py
    if not connected:
        content = "Cannot connect to server"
        showContent(content)
    else:
        send_log_out()

# back to logInMenu
def backToLogIn():
    gameScene.remove(gameLayer)
    initGameLayer()
    logIn_button = LogInMenu()
    gameLayer.add(logIn_button, z=20, name="logIn_button")

# 得到Server对logOut回应后do logOut
def doLogOut():
    gameScene.remove(gameLayer)
    initGameLayer()
    logIn_button = LogInMenu()
    gameLayer.add(logIn_button, z=20, name="logIn_button")

# choose difficulty
class DifficultyMenu(Menu):
    def __init__(self):
        super(DifficultyMenu, self).__init__()
        self.menu_valign = CENTER
        self.menu_halign = CENTER
        items = [
                (ImageMenuItem(common.load_image("button_simple.png"), self.selectSimple)),
                (ImageMenuItem(common.load_image("button_middle.png"), self.selectMiddle)),
                (ImageMenuItem(common.load_image("button_hard.png"), self.selectHard)),
                ]
        self.create_menu(items,selected_effect=zoom_in(),unselected_effect=zoom_out())

    def selectSimple(self):
        global game_difficulty
        game_difficulty = 1
        singleGameReady()

    def selectMiddle(self):
        global game_difficulty      
        game_difficulty = 2
        singleGameReady()

    def selectHard(self):
        global game_difficulty
        game_difficulty = 3
        singleGameReady()

# broadcast button from start_button
class NoticeInputMenu(Menu):
    def __init__(self):
        super(NoticeInputMenu, self).__init__()
        self.menu_valign = CENTER
        self.menu_halign = LEFT
        self.font_item['font_size'] = 20
        self.font_item_selected['font_size'] = 20
        items = [
                (EntryMenuItem('send:', getNotice, '', 20)),
                (ImageMenuItem(common.load_image("button_ok.png"), self.sendNotice)),
                (ImageMenuItem(common.load_image("button_back.png"), self.back))
                ]
        self.create_menu(items,selected_effect=zoom_out(),unselected_effect=zoom_out(),layout_strategy=myVerticalMenuLayout)

    def sendNotice(self):
        send_notice(notice_send, account)
        gameLayer.remove("notice_input_button")
        start_button = SingleGameStartMenu()
        gameLayer.add(start_button, z=20, name="start_button")

    def back(self):
        gameLayer.remove("notice_input_button")
        start_button = SingleGameStartMenu()
        gameLayer.add(start_button, z=20, name="start_button")

# single game start button的回调函数
def singleGameReady():
    removeContent()
    gameLayer.remove("difficulty_button")

    spriteBird = creatBird()
    gameLayer.add(spriteBird, z=20)

    ready = createAtlasSprite("text_ready")
    ready.position = (common.visibleSize["width"]/2, common.visibleSize["height"] * 3/4)

    tutorial = createAtlasSprite("tutorial")
    tutorial.position = (common.visibleSize["width"]/2, common.visibleSize["height"]/2)
    
    spriteBird.position = (common.visibleSize["width"]/3, spriteBird.position[1])

    #handling touch events
    class ReadyTouchHandler(cocos.layer.Layer):
        is_event_handler = True     #: enable director.window events

        def __init__(self):
            super( ReadyTouchHandler, self).__init__()

        def on_mouse_press (self, x, y, buttons, modifiers):
            """This function is called when any mouse button is pressed

            (x, y) are the physical coordinates of the mouse
            'buttons' is a bitwise or of pyglet.window.mouse constants LEFT, MIDDLE, RIGHT
            'modifiers' is a bitwise or of pyglet.window.key modifier constants
               (values like 'SHIFT', 'OPTION', 'ALT')
            """
            self.singleGameStart(buttons, x, y)
    
        # ready layer的回调函数
        def singleGameStart(self, eventType, x, y):
            global score, start_time
            isGamseStart = True
        
            spriteBird.gravity = gravity # gravity is from bird.py
            # handling bird touch events
            addTouchHandler(gameScene, isGamseStart, spriteBird)
            score = 0   #分数，飞过一个管子得到一分
            # add moving pipes
            pipes = createPipes(gameLayer, gameScene, spriteBird, score)
            # 小鸟AI初始化
            # initAI(gameLayer)
            # add score
            createScoreLayer(gameLayer)
            # add collision detect
            addCollision(gameScene, gameLayer, spriteBird, pipes, land_1, land_2)
            # remove startLayer
            gameScene.remove(readyLayer)

            pauseButton = PauseMenu()
            gameLayer.add(pauseButton, z=30, name="pause_button")

            start_time = time.time()

    readyLayer = ReadyTouchHandler()
    readyLayer.add(ready)
    readyLayer.add(tutorial)
    gameScene.add(readyLayer, z=10)

class PauseMenu(Menu):
    def __init__(self):
        super(PauseMenu, self).__init__()
        self.menu_valign = TOP
        self.menu_halign = RIGHT
        items = [
                (ImageMenuItem(common.load_image("button_pause.png"), pause))
                ]
        self.create_menu(items,selected_effect=zoom_in(),unselected_effect=zoom_out())

def pause():
    import cocos.scenes.pause as pause
    global pause_sc
    pause_sc = pause.get_pause_scene()
    if pause:
        director.push(pause_sc)
    resumeButton = ResumeMenu()
    pause_sc.add(resumeButton, z=20, name="resume_button")

class ResumeMenu(Menu):
    def __init__(self):
        super(ResumeMenu, self).__init__()
        self.menu_valign = TOP
        self.menu_halign = RIGHT
        items = [
                (ImageMenuItem(common.load_image("button_resume.png"), resume))
                ]
        self.create_menu(items,selected_effect=zoom_in(),unselected_effect=zoom_out())

def resume():
    global pause_sc
    pause_sc.remove("resume_button")
    director.pop()


def backToMainMenu():
    global end_time, total_time
    end_time = time.time()
    total_time = end_time - start_time
    total_time *= 1000000
    _total_time = int(total_time)

    if state == GUEST:
        # saveRecord('guest', '', pipe.g_score, _total_time, game_difficulty)
        restartButton = RestartMenu()
        gameLayer.add(restartButton, z=20, name="restart_button")
    else:
        send_score(account, password, pipe.g_score, _total_time, game_difficulty)
        request_champion(game_difficulty)
    # restartButton = RestartMenu()
    # gameLayer.add(restartButton, z=20, name="restart_button")

class RestartMenu(Menu):
    def __init__(self):
        super(RestartMenu, self).__init__()
        try:
            gameLayer.remove("pause_button")
        except Exception, e:
            pass
        self.menu_valign = CENTER  
        self.menu_halign = CENTER

        if state == GUEST:
            items = [
                    (ImageMenuItem(common.load_image("button_restart.png"), self.initMainMenu)),
                    (ImageMenuItem(common.load_image("button_backToLogIn.png"), backToLogIn))
                    ]  
            self.create_menu(items,selected_effect=zoom_in(),unselected_effect=zoom_out())
        else:
            items = [
                    (ImageMenuItem(common.load_image("button_restart.png"), self.initMainMenu)),
                    (ImageMenuItem(common.load_image("button_broadcast.png"), self.enterNotice)),
                    (ImageMenuItem(common.load_image("button_logOut.png"), logOut))
                    ]  
            self.create_menu(items,selected_effect=zoom_in(),unselected_effect=zoom_out())
            rank = createAtlasSprite("rank",0.8)
            rank.position = (common.visibleSize["width"]/2, common.visibleSize["height"] * 1/4)
            gameLayer.add(rank,z=20)

            # 2个label显示best name，用2个是为了显示的立体效果
            label = Label(text=championAccount, position=(common.visibleSize["width"]/2, common.visibleSize["height"] * 1/4-28))
            label.element.font_name = 'Hardpixel'
            label.element.font_size = 17
            label.element.color = (255,255,255,1000)
            gameLayer.add(label, z=50)

            label_3 = Label(text=championAccount, position=(common.visibleSize["width"]/2+1, common.visibleSize["height"] * 1/4-28+1))
            label_3.element.font_name = 'Hardpixel'
            label_3.element.font_size = 17
            label_3.element.color = (254,128,41,1000)
            gameLayer.add(label_3, z=51)

            # 2个label显示best score，用2个是为了显示的立体效果
            label_2 = Label(text=str(championScore), position=(common.visibleSize["width"]/2, common.visibleSize["height"] * 1/4))
            label_2.element.font_name = 'Hardpixel'
            label_2.element.font_size = 15
            label_2.element.color = (255,255,255,1000)
            gameLayer.add(label_2, z=50)

            label_4 = Label(text=str(championScore), position=(common.visibleSize["width"]/2+1, common.visibleSize["height"] * 1/4+1))
            label_4.element.font_name = 'Hardpixel'
            label_4.element.font_size = 15
            label_4.element.color = (254,128,41,1000)
            gameLayer.add(label_4, z=50)

    def initMainMenu(self):
        gameScene.remove(gameLayer)
        initGameLayer()
        isGamseStart = False
        difficulty_button = DifficultyMenu()
        gameLayer.add(difficulty_button, z=20, name="difficulty_button")

    def enterNotice(self):
        gameLayer.remove("restart_button")
        notice_input_button = NoticeInputMenu2()
        gameLayer.add(notice_input_button, z=20, name="notice_input_button")

# broadcast button from restart_button
class NoticeInputMenu2(Menu):
    def __init__(self):
        super(NoticeInputMenu2, self).__init__()
        self.menu_valign = CENTER
        self.menu_halign = LEFT
        self.font_item['font_size'] = 20
        self.font_item_selected['font_size'] = 20
        items = [
                (EntryMenuItem('send:', getNotice, '', 20)),
                (ImageMenuItem(common.load_image("button_ok.png"), self.sendNotice2)),
                (ImageMenuItem(common.load_image("button_back.png"), self.back2))
                ]
        self.create_menu(items,selected_effect=zoom_out(),unselected_effect=zoom_out(),layout_strategy=myVerticalMenuLayout)

    def sendNotice2(self):
        send_notice(notice_send, account)
        gameLayer.remove("notice_input_button")
        restart_button = RestartMenu()
        gameLayer.add(restart_button, z=20, name="restart_button")

    def back2(self):
        gameLayer.remove("notice_input_button")
        restart_button = RestartMenu()
        gameLayer.add(restart_button, z=20, name="restart_button")

def receive_champion(_name, _score):
    global championAccount, championScore
    print ('receive_champion', _name, _score)
    championAccount = _name
    championScore = _score
    restartButton = RestartMenu()
    gameLayer.add(restartButton, z=20, name="restart_button")

def showLogInMessange(_logInState):
    connected = connect(gameScene)  # connect is from network.py
    if not connected:
        content = "Cannot connect to server"
        showContent(content)
    else:
        gameLayer.remove("input_button")
        logInState = _logInState
        print("logInState:",_logInState)
        if logInState == 1:
            # removeContent()
            # gameLayer.remove("input_button")
            logIn_button = LogInMenu()
            gameLayer.add(logIn_button, z=20, name="logIn_button")
            content = "Name exist"
            showContent(content)
        elif logInState == 2:
            # gameLayer.remove("input_button")
            start_button = SingleGameStartMenu()
            gameLayer.add(start_button, z=20, name="start_button")
            content = "New account created"
            showContent(content)
        # elif logInState == 3:
        #     logIn_button = LogInMenu()
        #     gameLayer.add(logIn_button, z=20, name="logIn_button")
        #     content = "Account in black list"
        #     showContent(content)
        elif logInState == 6:
            # gameLayer.remove("input_button")
            logIn_button = LogInMenu()
            gameLayer.add(logIn_button, z=20, name="logIn_button")
            content = "No such account"
            showContent(content)
        elif logInState == 7:
            logIn_button = LogInMenu()
            gameLayer.add(logIn_button, z=20, name="logIn_button")
            content = "Account in black list"
            showContent(content)
        elif logInState == 8:
            # gameLayer.remove("input_button")
            logIn_button = LogInMenu()
            gameLayer.add(logIn_button, z=20, name="logIn_button")
            content = "Wrong passowrd"
            showContent(content)
        else:
            # gameLayer.remove("input_button")
            removeContent()
            start_button = SingleGameStartMenu()
            gameLayer.add(start_button, z=20, name="start_button")

def showContent(content):
    removeContent()
    notice = createLabel(content, common.visibleSize["width"]/2+5, common.visibleSize["height"] * 9/10)
    gameLayer.add(notice, z=70, name="content")

def removeContent():
    try:
        gameLayer.remove("content")
    except Exception, e:
        pass

def getDifficulty():
    return game_difficulty

def getNotice(value):
    global notice_send
    notice_send = value

def createLabel(value, x, y):
    label=Label(value, font_name='Times New Roman', font_size=15, color = (0,0,0,255), width = common.visibleSize["width"] - 20,
        multiline = True, anchor_x='center',anchor_y='center')
    label.position = (x, y)
    return label
