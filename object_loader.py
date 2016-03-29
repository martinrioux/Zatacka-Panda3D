import configs
from panda3d.core import LPoint3, TextNode, NodePath, Texture
from panda3d.core import TransparencyAttrib, LineSegs, GeomTristrips, Geom, GeomVertexArrayFormat, GeomVertexFormat
from direct.gui.DirectGui import DirectFrame, DGG, DirectButton, DirectCheckButton, DirectRadioButton

# import serial

def loadObject(tex=None, pos=LPoint3(0, 0), scale=1,
               transparency=True, model="models/plane"):

    obj = loader.loadModel(model)
    obj.reparentTo(render)
    obj.setPos(pos.getX(), 0, pos.getY())
    obj.setScale(scale)
    # obj.setBin("unsorted", 0)
    # obj.setDepthTest(False)
    obj.setTwoSided(True)

    if transparency:
        # Enable transparency blending.
        obj.setTransparency(TransparencyAttrib.MAlpha)

    if tex:
        # Load and set the requested texture.
        tex = loader.loadTexture("textures/" + tex)
        tex.setWrapU(Texture.WM_clamp)
        tex.setWrapV(Texture.WM_clamp)
        obj.setTexture(tex, 1)

    return obj

def create_button(self, label, position, color=(0,1,0,1)):
    text= TextNode('text') 
    text.setText(str("%s" % label))
    text.setTextColor(color)
    text.setAlign(TextNode.ACenter)
    # text.font = self.font
    text3d = NodePath(text) 
    text3d.setTwoSided(True)
    circle = loadObject(tex='circle.png')
    circle.reparentTo(text3d)
    circle.setPos(0.03,0,0.22)
    circle.setScale(0.7)
    text3d.setColorScale(color)
    circle.setColorScale(color)
    text3d.setAlphaScale(0.2)

    button=DirectFrame( 
                    enableEdit=1,      
                    geom=text3d,
                    borderWidth=(1,1), 
                    relief = None,
                    state=DGG.NORMAL,
                    parent=aspect2d
                    )
    button.setScale(0.11)
    button.setPos(position[0],0,position[1])

    button.bind(DGG.B1PRESS, button_click, [button, self])
    button.bind(DGG.WITHIN, button_hover, [button])
    button.bind(DGG.WITHOUT, button_no_hover, [button])
    # button.resetFrameSize()
    # self.button.bind(DGG.WITHIN, self.onMouseHoverInFunction, [button, some_value1])

    configs.ENTITIES[configs.ENTITY_ID] = {'CATEGORY':'button', 'BUTTON':button, 'NODE':text3d, 
    'LABEL':label,'STATUS': 0, 'COLOR':color, 'CIRCLE':circle, 'TEXT':text, 'R_NODE':None, 'L_NODE':None}
    configs.ENTITY_ID += 1
    entity = configs.ENTITIES[configs.ENTITY_ID-1]
    if isinstance(label, int) == True and configs.BUTTONS_MAP[label][0] != '' and configs.BUTTONS_MAP[label][1] != '':
        text= TextNode('text') 
        text.setText(configs.BUTTONS_MAP[label][0])
        text.setTextColor(entity['COLOR'])
        text.setAlign(TextNode.ACenter)
        text3d = NodePath(text) 
        text3d.setTwoSided(True)
        text3d.reparentTo(aspect2d)
        text3d.setPos(entity['BUTTON'],2,0,0.1)
        text3d.setColor(entity['COLOR'])
        text3d.setScale(0.08)    
        entity['L_NODE'] = text3d

        text= TextNode('text') 
        text.setText(configs.BUTTONS_MAP[label][1])
        text.setTextColor(entity['COLOR'])
        text.setAlign(TextNode.ACenter)
        text3d = NodePath(text) 
        text3d.setTwoSided(True)
        text3d.reparentTo(aspect2d)
        text3d.setPos(entity['BUTTON'],3.5,0,0.1)
        text3d.setColor(entity['COLOR'])
        text3d.setScale(0.08) 
        entity['R_NODE'] = text3d

        entity['BUTTON']["geom"] = None
        entity['NODE'].setAlphaScale(1)
        entity['BUTTON']["geom"] = entity['NODE']
    return entity

def create_label(self, text):
    textNode= TextNode('text') 
    textNode.setText(text)
    textNode.setTextColor(0,1,0,1)
    textNode.setAlign(TextNode.ACenter)
    text3d = NodePath(textNode) 
    text3d.setTwoSided(True)
    text3d.reparentTo(aspect2d)
    text3d.setColor(0,1,0,1)
    text3d.setScale(0.08) 
    return text3d

def button_click(self, button, panda3d):
    # sound = base.loader.loadSfx("sounds/click.ogg")
    # sound.play()
    if configs.MENU_LOCKED == True:
        return
    for entity_id, entity in configs.ENTITIES.items():
        if entity['CATEGORY'] == 'button' and entity['BUTTON'] == self:
            if entity['LABEL'] == 'S':
                configs.PANDA3D.init_game()
                return
            if entity['LABEL'] == 'Right Angle':
                if configs.FORCE_RIGHT_ANGLE_TURN == True:
                    configs.FORCE_RIGHT_ANGLE_TURN = False
                    entity['L_NODE'].hide()
                else:  
                    configs.FORCE_RIGHT_ANGLE_TURN = True
                    entity['L_NODE'].show()
                return

            if entity['LABEL'] == 'Arduino Mode':
                if configs.ARDUINO_MODE == True:
                    configs.ARDUINO_MODE = False
                    entity['L_NODE'].hide()
                else:  
                    connected = connectArduino(configs.PANDA3D)
                    if connected == True:
                        configs.ARDUINO_MODE = True
                        entity['L_NODE'].show()
                return


            if entity['LABEL'] == 'Line Gap':
                if configs.LINE_GAP == True:
                    configs.LINE_GAP = False
                    entity['L_NODE'].hide()
                else:  
                    configs.LINE_GAP = True
                    entity['L_NODE'].show()
                return
            if isinstance(entity['LABEL'], int) == True:

                width = 0.15
                height = 0.07
                ls = LineSegs("lines")
                ls.setColor(0,1,0,1)
                ls.drawTo(-width, 0, height)
                ls.drawTo(width, 0, height)
                ls.drawTo(width, 0,-height)
                ls.drawTo(-width, 0,-height)
                ls.drawTo(-width, 0, height)
                border = ls.create(False)
                border.setTag('back_ground', '1')
                self.border_node = NodePath("border")
                self.border_node.attachNewNode(border)
                self.border_node.reparentTo(aspect2d)
                self.border_node.setPos(entity['BUTTON'],3,0,0.2)
                try:
                    entity['R_NODE'].removeNode()
                except: 
                    print "nothing to remove"
                try:
                    entity['L_NODE'].removeNode()
                except: 
                    print "nothing to remove"
                configs.LAST_KEYSTROKE = ''
                taskMgr.add(input_button, "input", extraArgs=[self, entity_id, configs.LAST_KEYSTROKE, 'left'], appendTask=True) 
                configs.MENU_LOCKED = True

def button_hover(self, button):
    # sound = base.loader.loadSfx("sounds/rollover.ogg")
    # sound.play()
    for entity_id, entity in configs.ENTITIES.items():
        if entity['CATEGORY'] == 'button' and entity['BUTTON'] == self and entity['STATUS'] == 0:
            configs.PANDA3D.hover_circle.reparentTo(entity['BUTTON'])
            configs.PANDA3D.hover_circle.setPos(0.03,0,0.22)
            configs.PANDA3D.hover_circle.setColor(1,1,0,0.5)
            configs.PANDA3D.hover_circle.setScale(0.7)
            configs.PANDA3D.hover_circle.show()

def button_no_hover(self, button): 
    for entity_id, entity in configs.ENTITIES.items():
        if entity['CATEGORY'] == 'button' and entity['BUTTON'] == self and entity['STATUS'] == 0:
 
            configs.PANDA3D.hover_circle.hide()

def input_button(self, entity_id, last_key, which_key, task):
    entity = configs.ENTITIES[entity_id]
    if configs.ESC_PRESSED:
        entity['BUTTON']["geom"] = None
        entity['NODE'].setAlphaScale(0.2)
        entity['BUTTON']["geom"] = entity['NODE']
        try:
            entity['R_NODE'].removeNode()
        except: 
            print "nothing to remove"
        try:
            entity['L_NODE'].removeNode()
        except: 
            print "nothing to remove"
        configs.BUTTONS_MAP[entity['LABEL']][0] = ''
        configs.BUTTONS_MAP[entity['LABEL']][1] = ''
        self.border_node.removeNode()
        configs.MENU_LOCKED = False
        return task.done
    if last_key == configs.LAST_KEYSTROKE:
        return task.cont
    else:
        if which_key == 'left':

            text= TextNode('text') 
            text.setText(configs.LAST_KEYSTROKE)
            text.setTextColor(entity['COLOR'])
            text.setAlign(TextNode.ACenter)
            text3d = NodePath(text) 
            text3d.setTwoSided(True)
            text3d.reparentTo(aspect2d)
            text3d.setPos(entity['BUTTON'],2,0,0.1)
            text3d.setColor(entity['COLOR'])
            text3d.setScale(0.08)    
            entity['L_NODE'] = text3d

            configs.BUTTONS_MAP[entity['LABEL']][0] = configs.LAST_KEYSTROKE
            configs.LAST_KEYSTROKE = ''
            taskMgr.add(input_button, "input", extraArgs=[self, entity_id, configs.LAST_KEYSTROKE, 'right'], appendTask=True)

        else:
            text= TextNode('text') 
            text.setText(configs.LAST_KEYSTROKE)
            text.setTextColor(entity['COLOR'])
            text.setAlign(TextNode.ACenter)
            text3d = NodePath(text) 
            text3d.setTwoSided(True)
            text3d.reparentTo(aspect2d)
            text3d.setPos(entity['BUTTON'],3.5,0,0.1)
            text3d.setColor(entity['COLOR'])
            text3d.setScale(0.08) 
            entity['R_NODE'] = text3d

            self["geom"] = None
            entity['NODE'].setColorScale(entity['COLOR'])
            entity['CIRCLE'].setColorScale(entity['COLOR'])
            entity['TEXT'].setTextColor(entity['COLOR'])
            self["geom"] = entity['NODE']
            self.border_node.removeNode()
            configs.MENU_LOCKED = False
            entity['NODE'].setAlphaScale(1)
            configs.BUTTONS_MAP[entity['LABEL']][1] = configs.LAST_KEYSTROKE
            test_buttons(configs.PANDA3D, entity['LABEL'], configs.BUTTONS_MAP[entity['LABEL']][0], configs.BUTTONS_MAP[entity['LABEL']][1])

        return task.done

def test_buttons(self, label, l_btn, r_btn):
    for p in range(50):
        if configs.BUTTONS_MAP[p][0] == l_btn or configs.BUTTONS_MAP[p][0] == r_btn or configs.BUTTONS_MAP[p][1] == l_btn or configs.BUTTONS_MAP[p][1] == r_btn:
            if p != label:
                configs.BUTTONS_MAP[p][0] = ''
                configs.BUTTONS_MAP[p][1] = ''
                for entity_id, entity in configs.ENTITIES.items():
                    if entity['LABEL'] == p:
                        try:
                            entity['R_NODE'].removeNode()
                        except: 
                            print "nothing to remove"
                        try:
                            entity['L_NODE'].removeNode()
                        except: 
                            print "nothing to remove"
                        entity['BUTTON']["geom"] = None
                        entity['NODE'].setAlphaScale(0.2)
                        entity['BUTTON']["geom"] = entity['NODE']

def spawnButton(self):
    for i in range(25):
        color = configs.COLORS_MAP[i][0]
        y_pos = i%10 * (-0.18) + 0.8
        row = i // 10
        x_pos = row * 0.8 - 1.5
        create_button(self, i, (x_pos, y_pos), color)

    button = create_button(self, '', (1.4, -0.7), (0,1,0,1))
    button['LABEL'] = 'S'
    button['R_NODE'] = create_label(self, 'Start')
    button['R_NODE'].setPos(button['BUTTON'], -2,0,0)

    button = create_button(self, '', (1.4, -0.5), (0,1,0,1))
    button['LABEL'] = 'Right Angle'
    button['R_NODE'] = create_label(self, 'Right Angle')
    button['R_NODE'].setPos(button['BUTTON'], -3,0,0)
    button['L_NODE'] = create_label(self, 'X')
    button['L_NODE'].setPos(button['BUTTON'], 0,0,0)
    button['L_NODE'].hide()
    if configs.FORCE_RIGHT_ANGLE_TURN == True:
        button['L_NODE'].show()

    button = create_button(self, '', (1.4, -0.3), (0,1,0,1))
    button['LABEL'] = 'Line Gap'
    button['R_NODE'] = create_label(self, 'Line Gap')
    button['R_NODE'].setPos(button['BUTTON'], -2.7,0,0)
    button['L_NODE'] = create_label(self, 'X')
    button['L_NODE'].setPos(button['BUTTON'], 0,0,0)
    button['L_NODE'].hide()
    if configs.LINE_GAP == True:
        button['L_NODE'].show()

    configs.ARDUINO_PLAYER_ON = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    configs.IN_MENU = True
    for i in range(50):
        configs.ARDUINO_BUTTONS_MAP[i] = [False, False]
