# -*- coding: utf-8 -*-
from cocos.actions import *
from atlas import *
import common
#两个相连接地面，不断循环向左移动一个屏宽，再回到原点
# def createLand():
#     landHeight = atlas["land"]["height"]/4
    
#     #first moving land
#     land_1 = createAtlasSprite("land")
#     land_1.position = common.visibleSize["width"] / 2, landHeight

#     move1 = MoveTo((- common.visibleSize["width"]/ 2, landHeight), 2)
#     reset1 = Place((common.visibleSize["width"]/ 2, landHeight))
#     land_1.do(Repeat(sequence(move1, reset1)))

#     #second moving land
#     land_2 = createAtlasSprite("land")
#     land_2.position = common.visibleSize["width"] * 3 / 2, landHeight

#     move2 = MoveTo((common.visibleSize["width"] / 2, landHeight), 2)
#     reset2 = Place((common.visibleSize["width"] * 3 / 2, landHeight))

#     land_2.do(Repeat(sequence(move2, reset2)))
    
#     return land_1, land_2

#一个land绿条的单位长度=24
def createLand():
    landHeight = atlas["land"]["height"]/4 #取land的高度的1/4
    
    #first moving land
    land_1 = createAtlasSprite("land")
    # land_1.position = common.visibleSize["width"] / 2, landHeight #纵坐标不变，横坐标左移一半
    land_1.position = 168, landHeight #纵坐标不变，横坐标左移一半

    # move1 = MoveTo((- common.visibleSize["width"]/ 2, landHeight), 2) #移动坐标，移动时间
    move1 = MoveTo((168-96, landHeight), 1) #移动坐标，移动时间
    # reset1 = Place((common.visibleSize["width"]/ 2, landHeight))
    reset1 = Place((168, landHeight))
    land_1.do(Repeat(sequence(move1, reset1)))

    #second moving land
    land_2 = createAtlasSprite("land")
    # land_2.position = common.visibleSize["width"] * 3 / 2, landHeight
    land_2.position = 168+48, landHeight

    # move2 = MoveTo((common.visibleSize["width"] / 2, landHeight), 2)
    move2 = MoveTo((168-96+48, landHeight), 1)
    # reset2 = Place((common.visibleSize["width"] * 3 / 2, landHeight))
    reset2 = Place((168+48, landHeight))

    land_2.do(Repeat(sequence(move2, reset2)))
    
    return land_1, land_2