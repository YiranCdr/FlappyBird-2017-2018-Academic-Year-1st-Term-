# -*- coding: utf-8 -*-
import cocos
import time
from cocos.scene import *
from cocos.actions import *
from cocos.layer import *
from cocos.text import *
from cocos.menu import *
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
from pyglet import font
from pyglet.window import key

###
# 按resume时的点击应该是不跳的
# 
#####################
game_diffficulty = 0

#####################
# vars
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

REGISTER = 1
LOG_IN = 2
state = 0
isSuccess = 0
real_password = '123'
real_account = '123'

start_time = None
end_time = None
total_time = None

championAccount = 'a'
championScore = '1'


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


def initGameLayer():
	global spriteBird, gameLayer, land_1, land_2
	# gameLayer: 游戏场景所在的layer
	gameLayer = Layer()
	# add background
	bg = createAtlasSprite("bg_day")
	bg.position = (common.visibleSize["width"] / 2, common.visibleSize["height"] / 2)
	gameLayer.add(bg, z=0)
	# add moving bird
	# spriteBird = creatBird()
	# gameLayer.add(spriteBird, z=20)
	# add moving land
	land_1, land_2 = createLand()
	gameLayer.add(land_1, z=10)
	gameLayer.add(land_2, z=10)
	# add gameLayer to gameScene
	gameScene.add(gameLayer)


def game_start(_gameScene):
	global gameScene
	# 给gameScene赋值
	gameScene = _gameScene
	initGameLayer()
	# start_botton = SingleGameStartMenu()
	# gameLayer.add(start_botton, z=20, name="start_button")
	connect(gameScene)
	logIn_button = LogInMenu()
	gameLayer.add(logIn_button, z=20, name="logIn_button")


def createLabel(value, x, y):
	label = Label(value,
				  font_name='Times New Roman',
				  font_size=15,
				  color=(0, 0, 0, 255),
				  width=common.visibleSize["width"] - 20,
				  multiline=True,
				  anchor_x='center', anchor_y='center')
	label.position = (x, y)
	return label


# single game start button的回调函数
def singleGameReady():
	removeContent()
	gameLayer.remove("difficulty_button")

	spriteBird = creatBird()
	gameLayer.add(spriteBird, z=20)

	ready = createAtlasSprite("text_ready")
	ready.position = (common.visibleSize["width"] / 2, common.visibleSize["height"] * 3 / 4)

	tutorial = createAtlasSprite("tutorial")
	tutorial.position = (common.visibleSize["width"] / 2, common.visibleSize["height"] / 2)

	spriteBird.position = (common.visibleSize["width"] / 3, spriteBird.position[1])

	# handling touch events
	class ReadyTouchHandler(cocos.layer.Layer):
		is_event_handler = True  #: enable director.window events

		def __init__(self):
			super(ReadyTouchHandler, self).__init__()

		def on_mouse_press(self, x, y, buttons, modifiers):
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

			spriteBird.gravity = gravity  # gravity is from bird.py
			# handling bird touch events
			addTouchHandler(gameScene, isGamseStart, spriteBird)
			score = 0  # 分数，飞过一个管子得到一分
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

			################################
			pauseButton = PauseMenu()
			gameLayer.add(pauseButton, z=30, name="pause_button")
			################################
			start_time = time.time()

	readyLayer = ReadyTouchHandler()
	readyLayer.add(ready)
	readyLayer.add(tutorial)
	gameScene.add(readyLayer, z=10)


def backToMainMenu():
	global end_time, total_time
	end_time = time.time()
	total_time = end_time - start_time
	total_time *= 1000000
	_total_time = int(total_time)
	send_score(account, password, pipe.g_score, _total_time, game_diffficulty)
	request_champion(game_diffficulty)


# restartButton = RestartMenu()
# gameLayer.add(restartButton, z=20, name="restart_button")


def receive_champion(_name, _score):
	global championAccount, championScore
	print ('receive_champion', _name, _score)
	championAccount = _name
	championScore = _score
	restartButton = RestartMenu()
	gameLayer.add(restartButton, z=20, name="restart_button")


def sendLogInMessange(_logInState):
	connected = connect(gameScene)  # connect is from network.py
	if not connected:
		content = "Cannot connect to server"
		showContent(content)
	else:
		gameLayer.remove("input_button")
		logInState = _logInState
		print("logInState:", _logInState)
		if logInState == 1:
			# removeContent()
			# gameLayer.remove("input_button")
			logIn_button = LogInMenu()
			gameLayer.add(logIn_button, z=20, name="logIn_button")
			content = "Existed"
			showContent(content)
		elif logInState == 2:
			# gameLayer.remove("input_button")
			start_button = SingleGameStartMenu()
			gameLayer.add(start_button, z=20, name="start_button")
			content = "Create"
			showContent(content)
		elif logInState == 7:
			# gameLayer.remove("input_button")
			logIn_button = LogInMenu()
			gameLayer.add(logIn_button, z=20, name="logIn_button")
			content = "No Such Input"
			showContent(content)
		elif logInState == 8:
			# gameLayer.remove("input_button")
			logIn_button = LogInMenu()
			gameLayer.add(logIn_button, z=20, name="logIn_button")
			content = "Wrong"
			showContent(content)
		else:
			# gameLayer.remove("input_button")
			removeContent()
			start_button = SingleGameStartMenu()
			gameLayer.add(start_button, z=20, name="start_button")
		# content = "haha"
		# showContent(content)
	# send_log_in_message(state, account, password)


def logOut():
	global gameScene, gameLayer
	connected = connect(gameScene)  # connect is from network.py
	if not connected:
		content = "Cannot connect to server"
		showContent(content)
	else:
		send_log_out()
	# gameScene.remove(gameLayer)
	# initGameLayer()
	# logIn_button = LogInMenu()
	# gameLayer.add(logIn_button, z=20, name="logIn_button")


def doLogOut():
	gameScene.remove(gameLayer)
	initGameLayer()
	logIn_button = LogInMenu()
	gameLayer.add(logIn_button, z=20, name="logIn_button")


# def logIn():
# 	removeContent()
# 	gameLayer.remove("start_button")
# 	gameLayer.remove(spriteBird)
# 	logIn_button = LogInMenu()
# 	gameLayer.add(logIn_button, z=20, name="logIn_button")


def showNotice():
	connected = connect(gameScene)  # connect is from network.py
	if not connected:
		content = "Cannot connect to server"
		showContent(content)
	else:
		request_notice()  # request_notice is from network.py


def showContent(content):
	removeContent()
	notice = createLabel(content, common.visibleSize["width"] / 2 + 5, common.visibleSize["height"] * 9 / 10)
	gameLayer.add(notice, z=70, name="content")


def removeContent():
	try:
		gameLayer.remove("content")
	except Exception, e:
		pass


class LogInMenu(Menu):

	def __init__(self):
		super(LogInMenu, self).__init__()
		self.menu_valign = CENTER
		self.menu_halign = CENTER
		items = [
			(ImageMenuItem(common.load_image("button_register.png"), register)),
			(ImageMenuItem(common.load_image("button_logIn.png"), logIn)),
			(ImageMenuItem(common.load_image("button_exit.png"), exit))
		]

		self.create_menu(items, selected_effect=zoom_in(), unselected_effect=zoom_out())


def exit():
	gameScene.end()


#   def on_entry(self, value):
#   	global account
#   	account += value
#   print 'entry item callback', value

#   def getInput(self):
#   	enter_button = Settings()
#   	gameLayer.add(enter_button, z=50,name="enter_button")

#   def back(self):
# gameLayer.remove("logIn_button")
# startButton = SingleGameStartMenu()
# gameLayer.add(startButton, z=50, name="start_button")

class RestartMenu(Menu):
	def __init__(self):
		super(RestartMenu, self).__init__()
		gameLayer.remove("pause_button")
		self.menu_valign = CENTER
		self.menu_halign = CENTER
		items = [
			(ImageMenuItem(common.load_image("button_restart.png"), self.initMainMenu)),
			(ImageMenuItem(common.load_image("button_notice.png"), showNotice)),
			(ImageMenuItem(common.load_image("button_logOut.png"), logOut))
		]
		self.create_menu(items, selected_effect=zoom_in(), unselected_effect=zoom_out())
		rank = createAtlasSprite("rank", 0.8)
		rank.position = (common.visibleSize["width"] / 2, common.visibleSize["height"] * 1 / 4)
		gameLayer.add(rank, z=20)
		scoreStr = str(pipe.g_score)
		i = 0
		for d in scoreStr:
			s = createAtlasSprite("number_score_0" + d)
			s.position = common.visibleSize["width"] / 2 + 18 * i + 25, common.visibleSize["height"] * 1 / 4 + 23
			i = i + 1
			gameLayer.add(s, z=30)
		label = Label(text=championAccount + '  ' + str(championScore),
					  position=(common.visibleSize["width"] / 2, common.visibleSize["height"] * 1 / 4 - 30))
		# ,font_size=25,color=(0,0,0,0)
		label.element.font_size = 25
		label.element.color = (0, 0, 0, 1000)
		gameLayer.add(label, z=50)

	def initMainMenu(self):
		gameScene.remove(gameLayer)
		initGameLayer()
		isGamseStart = False
		difficulty_button = DifficultyMenu()
		gameLayer.add(difficulty_button, z=20, name="difficulty_button")


class SingleGameStartMenu(Menu):
	def __init__(self):
		super(SingleGameStartMenu, self).__init__()
		self.menu_valign = CENTER
		self.menu_halign = CENTER
		items = [
			(ImageMenuItem(common.load_image("button_start.png"), self.gameStart)),
			(ImageMenuItem(common.load_image("button_notice.png"), showNotice)),
			(ImageMenuItem(common.load_image("button_logOut.png"), logOut))
		]
		self.create_menu(items, selected_effect=zoom_in(), unselected_effect=zoom_out())

	def gameStart(self):
		gameLayer.remove("start_button")
		difficulty_button = DifficultyMenu()
		gameLayer.add(difficulty_button, z=20, name="difficulty_button")
	# singleGameReady()


class ResumeMenu(Menu):
	def __init__(self):
		super(ResumeMenu, self).__init__()
		self.menu_valign = TOP
		self.menu_halign = RIGHT
		items = [
			(ImageMenuItem(common.load_image("button_resume.png"), resume))
		]
		self.create_menu(items, selected_effect=zoom_in(), unselected_effect=zoom_out())


def resume():
	global pause_sc
	pause_sc.remove("resume_button")
	director.pop()


class PauseMenu(Menu):
	def __init__(self):
		super(PauseMenu, self).__init__()
		self.menu_valign = TOP
		self.menu_halign = RIGHT
		items = [
			(ImageMenuItem(common.load_image("button_pause.png"), pause))
		]
		self.create_menu(items, selected_effect=zoom_in(), unselected_effect=zoom_out())


class InputMenu(Menu):
	def __init__(self):
		# global account, password
		super(InputMenu, self).__init__()
		self.menu_valign = CENTER
		self.menu_halign = CENTER
		self.font_item['font_size'] = 10
		self.font_item_selected['font_size'] = 20
		items = [
			(EntryMenuItem('Account:', getName, '', 10)),
			(myEntryMenuItem('Password:', getPassword, '', 20)),
			(ImageMenuItem(common.load_image("button_ok.png"), checkInputAnd)),
		]
		self.create_menu(items, selected_effect=zoom_out(), unselected_effect=zoom_out(), layout_strategy = myVerticalMenuLayout)


class Broadcast(Menu):
	def __init__(self):
		super(Broadcast, self).__init__()
		self.menu_valign = CENTER
		self.menu_halign = CENTER
		self.font_item['font_size'] = 10
		self.font_item_selected['font_size'] = 20
		items = [
			(EntryMenuItem('', ))
		]

class DifficultyMenu(Menu):
	def __init__(self):
		# global account, password
		super(DifficultyMenu, self).__init__()
		self.menu_valign = CENTER
		self.menu_halign = CENTER
		items = [
			(ImageMenuItem(common.load_image("button_simple.png"), selectSimple)),
			(ImageMenuItem(common.load_image("button_middle.png"), selectMiddle)),
			(ImageMenuItem(common.load_image("button_hard.png"), selectHard)),
		]
		self.create_menu(items, selected_effect=zoom_in(), unselected_effect=zoom_out())


def selectSimple():
	global game_diffficulty
	game_diffficulty = 1
	singleGameReady()


def selectMiddle():
	global game_diffficulty
	game_diffficulty = 2
	singleGameReady()


def selectHard():
	global game_diffficulty
	game_diffficulty = 3
	singleGameReady()


def getName(value):
	global account
	account = value


def getPassword(value):
	global password
	password = value


def checkInputAnd():
	print account
	print password
	send_log_in_message(state, account, password)


# global state
# if state == LOG_IN:
# content = "logIn"
# showContent(content)
# elif state == REGISTER:
# content = "register"
# showContent(content)
# gameLayer.remove("input_button")


def pause():
	import cocos.scenes.pause as pause
	global pause_sc
	pause_sc = pause.get_pause_scene()
	if pause:
		director.push(pause_sc)
	resumeButton = ResumeMenu()
	pause_sc.add(resumeButton, z=20, name="resume_button")


def getDifficulty():
	return game_diffficulty


def register():
	global state
	state = REGISTER
	gameLayer.remove("logIn_button")
	input_button = InputMenu()
	gameLayer.add(input_button, z=20, name="input_button")


def logIn():
	global state
	state = LOG_IN
	gameLayer.remove("logIn_button")
	input_button = InputMenu()
	gameLayer.add(input_button, z=20, name="input_button")
