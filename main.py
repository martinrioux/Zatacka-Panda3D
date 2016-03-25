#!/usr/bin/env python

import configs
configs.init_defines() 

from object_loader import loadObject, create_button, spawnButton
from panda3d.core import WindowProperties, Vec3, LVector3f, TransparencyAttrib
from direct.task.Task import Task

from players import update_players, init_player
# from players import test_collisions, create_dots
from graphics import start_new_line, draw_line

from direct.showbase.ShowBase import ShowBase
from direct.interval.LerpInterval import LerpPosInterval, LerpHprInterval

from bonus import spawn_bonus, init_bonus_tasks
import random
import sys
import copy
from panda3d.core import PStatCollector, PStatClient, Shader

class zatacka(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)

        self.enableParticles()
        # self.setFrameRateMeter(True)
        wp = WindowProperties()
        wp.setSize(1280, 720)
        wp.setFullscreen(False)
        self.win.requestProperties(wp)
        self.disableMouse()
        self.camLens.setNear(0.01)
        # Load the background starfield.
        # self.font = loader.loadFont('textures/inconsolata.egg')

        self.setBackgroundColor((0, 0, 0, 1))
        self.cameraPivot = render.attachNewNode("CameraPivot")
        self.cameraArm = self.cameraPivot.attachNewNode("CameraArm")
        self.cameraArm.setPos(self.cameraArm, 0,-4.1,0)
        self.camera.reparentTo(self.cameraArm)
        # self.camera.lookAt(self.cameraPivot)
        # self.keys = {   "turnLeft": 0, 
        #                 "turnRight": 0,
        #             }
        # PStatClient.connect()
        # Other keys events set the appropriate value in our key dictionary
        base.buttonThrowers[0].node().setKeystrokeEvent('keystroke')

        configs.PANDA3D = self
        self.accept('f6', self.changeCamera)
        self.accept('keystroke', self.getKeys)
        self.accept('escape', self.set_esc, [1])
        self.accept('escape-up', self.set_esc, [0])
        
        configs.COLLISION_MAP = [[[0,0,0] for x in range(825)] for x in range(1385)] 
        # init_menu(self)
        # self.gameTask = taskMgr.add(self.menuLoop, "gameLoop")
        self.gameBoard = loadObject()
        self.gameBoard.setColor(0.3,0.3,0.3,0.5)
        self.gameBoard.setScale(1)
        self.gameBoard.setSx(1.8)
        self.gameBoard.setPos(0,0.02,0)
        self.border = loader.loadModel("models/border")
        self.border.reparentTo(render)
        self.border.setPos(0,0,0)
        self.border.setPos(0,0,0)
        self.border.setP(90)
        self.border.setScale(0.0028)
        self.border.setSz(0.001)
        self.border.setSx(0.00282)
        self.border.setSy(0.00279)
        self.border.setTransparency(TransparencyAttrib.MAlpha)
        self.border.setColorScale(0, 1, 0, 1.0)

        self.hover_circle = loadObject(tex='circle.png')
        self.hover_circle.hide()

        init_bonus_tasks(self)

        # display_shader = Shader.load(Shader.SL_GLSL, vertex="shaders/display_shader.vert", fragment="shaders/display_shader.frag")
        # self.render.set_shader(display_shader)

        self.init_menu()

    def getKeys(self, keyname):
        configs.LAST_KEYSTROKE = keyname

    def set_esc(self, value):
        configs.ESC_PRESSED = value

    def init_menu(self):
        interval = LerpHprInterval(self.cameraPivot, 1, (0,0,0), (0,10,0))
        interval2 = LerpPosInterval(self.cameraPivot, 1, (0,0,0), (0,0,-0.05))
        interval.start()
        interval2.start()
        taskMgr.doMethodLater(1, spawnButton, "spawnButton")         

    def init_game(self):
        configs.IN_MENU = False
        interval = LerpHprInterval(self.cameraPivot, 1, (0,10,0), (0,0,0))
        interval2 = LerpPosInterval(self.cameraPivot, 1, (0,0,-0.05), (0,0,0))
        interval.start()
        interval2.start()
        for entity_id, entity in configs.ENTITIES.items():
            if entity['CATEGORY'] == 'button':
                entity['BUTTON'].destroy()
                try:
                    entity['R_NODE'].removeNode()
                except: 
                    print "nothing to remove"
                try:
                    entity['L_NODE'].removeNode()
                except: 
                    print "nothing to remove"
            del(configs.ENTITIES[entity_id])
        used_positions = []
        for p in range(25):
            position = (random.uniform(-1.6, 1.6), 0, random.uniform(-0.8, 0.8))
            heading = random.randint(0,360)
            empty_space = False
            while empty_space == False:
                empty_space = True
                for other_position in used_positions:
                    distance = pow(pow((other_position[0] - position[0]),2) + pow((other_position[2] - position[2]),2),0.5)
                    if distance < 0.25:
                        empty_space = False
                        position = (random.uniform(-1.6, 1.6), 0, random.uniform(-0.8, 0.8))

            btn_left = configs.BUTTONS_MAP[p][0]
            btn_right = configs.BUTTONS_MAP[p][1]
            if (btn_right == '' or btn_left == '') and configs.ARDUINO_PLAYER_ON[p] == 0:
                continue
            used_positions += [position]
            init_player(self, btn_left, btn_right, p, pos=position, heading=heading)
        
        configs.BONUS_START_TIME[2] = globalClock.getFrameTime()

        if used_positions == []:
            self.init_menu()
        else:
            self.countDown = taskMgr.add(countDown, "countDown", extraArgs=[self, 5], appendTask=True) 
            self.gameTask = taskMgr.add(self.gameLoop, "gameLoop") 
  
        # self.draw_lines = taskMgr.doMethodLater(0.05, draw_lines, 'draw lines', extraArgs=[self], appendTask=True) 
        # self.create_dots = taskMgr.doMethodLater(0.001, create_dots, 'create_dot', extraArgs=[self], appendTask=True)

    def setKey(self, key, val):
        self.keys[key] = val

        
    def changeCamera(self):    
        self.oobe()
       
    def gameLoop(self, task):
        dt = globalClock.getDt()
        if configs.GAME_ONGOING == 0:
            return Task.cont
        else:
            update_players(self, dt)
            return Task.cont   

    def reset_game(self, self1):
        taskMgr.remove('gameLoop')
        taskMgr.remove('bonusSpawner')
        for entity_id, entity in configs.ENTITIES.items():
            if entity['CATEGORY'] == 'player':
                no = entity['PLAYER_NUMBER']
                left_btn = configs.BUTTONS_MAP[no][0]
                right_btn = configs.BUTTONS_MAP[no][1]
                self.ignore("%s" % left_btn)
                self.ignore("%s-up" % left_btn)
                self.ignore("%s" % right_btn)
                self.ignore("%s-up" % right_btn)
                entity['NODE'].removeNode()
                entity['PARTICLE_PARENT'].disable()
                entity['PARTICLE_PARENT'].reset()
            if entity['CATEGORY'] == 'bonus':
                entity['NODE'].removeNode()
            if entity['CATEGORY'] == 'line':
                entity['NODE'].removeNode()
            del(configs.ENTITIES[entity_id])
        self.winner.removeNode()
        configs.BONUS_START_TIME[2] = globalClock.getFrameTime()
        configs.GAME_WON = False
        configs.GAME_ONGOING = 0
        self.init_menu()

def countDown(self, number, task):
    if number == 5:
        print 5
        self.count_down = loadObject('5.png')
        self.count_down.setPos(0,0.1,0)
        self.count_down.setScale(configs.SCALE*0.1)
        self.count_down.setAlphaScale(1)
        taskMgr.doMethodLater(1, countDown, 'draw lines', extraArgs=[self, 4], appendTask=True) 
    if number == 4:
        self.count_down.removeNode()
        print 4
        self.count_down = loadObject('4.png')
        self.count_down.setPos(0,0.1,0)
        self.count_down.setScale(configs.SCALE*0.1)
        self.count_down.setAlphaScale(1)
        taskMgr.doMethodLater(1, countDown, 'draw lines', extraArgs=[self, 3], appendTask=True) 
    if number == 3:
        self.count_down.removeNode()
        self.count_down = loadObject('3.png')
        self.count_down.setPos(0,0.1,0)
        self.count_down.setScale(configs.SCALE*0.1)
        self.count_down.setAlphaScale(1)
        print 3
        taskMgr.doMethodLater(1, countDown, 'draw lines', extraArgs=[self, 2], appendTask=True) 
    if number == 2:
        self.count_down.removeNode()
        self.count_down = loadObject('2.png')
        self.count_down.setPos(0,0.1,0)
        self.count_down.setScale(configs.SCALE*0.1)
        self.count_down.setAlphaScale(1)
        print 2
        taskMgr.doMethodLater(1, countDown, 'draw lines', extraArgs=[self, 1], appendTask=True) 
    if number == 1:
        self.count_down.removeNode()
        self.count_down = loadObject('1.png')
        self.count_down.setPos(0,0.1,0)
        self.count_down.setScale(configs.SCALE*0.1)
        self.count_down.setAlphaScale(1)
        print 1
        for entity_id, entity in configs.ENTITIES.items():
            if entity['CATEGORY'] == 'player':
                entity['PLAYER_ID'].detachNode()
                entity['CIRCLE_NODE'].detachNode()
        taskMgr.doMethodLater(1, countDown, 'draw lines', extraArgs=[self, 0], appendTask=True) 
    if number == 0:
        print 0
        self.count_down.removeNode()
        for entity_id, entity in configs.ENTITIES.items():
            if entity['CATEGORY'] == 'player':
                configs.GAME_ONGOING = 1
                new_line, line_vertex, line_node = start_new_line(self, entity['NODE'].getX(), entity['NODE'].getZ(), entity['COLOR'])
                line_id = configs.ENTITY_ID
                configs.ENTITIES[configs.ENTITY_ID] = {'CATEGORY':'line', 'GEOM':new_line, 'VERTEX':line_vertex, 'NODE': line_node}
                configs.ENTITY_ID += 1
                entity["CURRENT_LINE"] = line_id
                draw_line(entity_id, start=True)     
                configs.NEXT_BONUS_TIME = globalClock.getFrameTime() + random.randint(3, 10)
                self.spawn_bonus = taskMgr.add(spawn_bonus, 'bonusSpawner', extraArgs=[self], appendTask=True)
    return task.done


game = zatacka()
game.run()