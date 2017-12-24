# -*- coding: utf-8 -*-
from cocos.actions import *
from cocos.cocosnode import *
from cocos.collision_model import *
import random
from atlas import *
from bird import *
from score import *
import game_controller
from game_controller import *
import common
from file_operation_level import *
import time

#######################
#pipeDistance要改为[]
#######################
# constants
pipeCount = 2
pipeHeight = 320
pipeWidth = 52
# pipeDistance = 100    #上下管道间的距离
pipeDistance = [100,100]    #上下管道间的距离
pipeInterval = 180    #两根管道的水平距离
waitDistance = 100   #开始时第一根管道距离屏幕最右侧的距离
heightOffset = 25     #管道的高度偏移值
# vars
PIPE_NEW = 0
PIPE_PASS = 1
pipes = {}    #contains nodes of pipes
pipeState = {}    #PIPE_NEW or PIPE_PASS
downPipeYPosition = {}    #朝下pipe的最下侧的y坐标
upPipeYPosition = {}  #朝上pipe的最上侧的y坐标
pipeIndex = 0

class ActorModel(object):
    def __init__(self, cx, cy, half_width, half_height,name):
            self.cshape = CircleShape(eu.Vector2(center_x, center_y), radius)
            self.name = name

def createPipes(layer, gameScene, spriteBird, score):
    global g_score, movePipeFunc, calScoreFunc, difficulty
    difficulty = game_controller.getDifficulty()
    def initPipe():
        global g_score, moveDistance, pipeInterval, difficulty, pipeDistance
        if difficulty == 1:
            moveDistance = 1.5  # 速度
            pipeInterval = 250
        elif difficulty == 2:
            moveDistance = 1.9
            pipeInterval = 220
        else:
            moveDistance = 2.3
            pipeInterval = 190
        for i in range(0, pipeCount):
            pipeDistance[i] = 150 - 15 * difficulty + random.randint(0, 20)
            #把downPipe和upPipe组合为singlePipe
            downPipe = CollidableRectSprite("pipe_down", 0, (pipeHeight + pipeDistance[i]), pipeWidth/2, pipeHeight/2) #朝下的pipe而非在下方的pipe
            upPipe = CollidableRectSprite("pipe_up", 0, 0, pipeWidth/2, pipeHeight/2)  #朝上的pipe而非在上方的pipe
            singlePipe = CocosNode()
            singlePipe.add(downPipe, name="downPipe")
            singlePipe.add(upPipe, name="upPipe")
            
            #设置管道高度和位置
            center = random.randint(170, 400)
            singlePipe.position=(common.visibleSize["width"] + i*pipeInterval + waitDistance, center - pipeHeight/2 - pipeDistance[i]/2)
            layer.add(singlePipe, z=5)
            pipes[i] = singlePipe
            pipeState[i] = PIPE_NEW
            upPipeYPosition[i] = center - pipeDistance[i]/2
            downPipeYPosition[i] = center + pipeDistance[i]/2

    def movePipe(dt):
        global g_score, moveDistance, pipeInterval, difficulty, pipeDistance
        
        
        for i in range(0, pipeCount):
            
            pipes[i].position = (pipes[i].position[0]-moveDistance, pipes[i].position[1])
            if pipes[i].position[0] < -pipeWidth/2:
                pipeNode = pipes[i]
                pipeState[i] = PIPE_NEW
                ###########################
                pipeDistance[i] = 150 - 15 * difficulty + random.randint(0, 20)
                center = random.randint(170, 400) # center为上下水管的纵坐标的中心位置
                pipeNode.get('downPipe').position = (0, pipeDistance[i] + pipeHeight)
                pipeNode.get('downPipe').cshape.center = (0, pipeDistance[i] + pipeHeight) 
                pipeNode.position = (0, center - pipeHeight/2 - pipeDistance[i]/2)
                upPipeYPosition[i] = center - pipeDistance[i]/2
                downPipeYPosition[i] = center + pipeDistance[i]/2
                #####################################
                next = i - 1
                if next < 0: next = pipeCount - 1
                pipeNode.position = (pipes[next].position[0] + pipeInterval, center - pipeHeight/2 - pipeDistance[i]/2)
                # upPipeYPosition[i] = heightOffset + pipeHeight/2
                # downPipeYPosition[i] = heightOffset + pipeHeight/2 + pipeDistance[i]
                break

    def calScore(dt):
        global g_score
        birdXPosition = spriteBird.position[0]
        for i in range(0, pipeCount):
            if pipeState[i] == PIPE_NEW and pipes[i].position[0]< birdXPosition:
                pipeState[i] = PIPE_PASS
                g_score = g_score + 1
                
                tmp_time = time.time()
                tmp_total_time = tmp_time - game_controller.start_time
                tmp_total_time *= 1000000
                _tmp_total_time = int(tmp_total_time)
                _tmp_total_time_str = str(_tmp_total_time)
                # print("_tmp_total_time_str", _tmp_total_time_str)
                if game_controller.state == game_controller.GUEST:
                    saveRecord('guest', '', g_score, _tmp_total_time_str, game_controller.game_difficulty)
                else:
                    saveRecord(game_controller.account, game_controller.password, g_score, _tmp_total_time_str, game_controller.game_difficulty)
                setSpriteScores(g_score) #show score on top of screen
    
    g_score = score
    initPipe()
    movePipeFunc = movePipe
    calScoreFunc = calScore
    gameScene.schedule(movePipe)
    gameScene.schedule(calScore)
    return pipes

def removeMovePipeFunc(gameScene):
    global movePipeFunc
    if movePipeFunc != None:
        gameScene.unschedule(movePipeFunc)

def removeCalScoreFunc(gameScene):
    global calScoreFunc
    if calScoreFunc != None:
        gameScene.unschedule(calScoreFunc)

def getPipes():
    return pipes

def getUpPipeYPosition():
    return upPipeYPosition

def getPipeCount():
    return pipeCount

def getPipeWidth():
    return pipeWidth

def getPipeDistance():
    return pipeDistance