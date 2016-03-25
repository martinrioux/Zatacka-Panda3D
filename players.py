import configs 
from math import pi, cos, sin
from panda3d.core import TransparencyAttrib, LineSegs, GeomTristrips, Geom, GeomVertexArrayFormat, GeomVertexFormat
from panda3d.core import GeomVertexData, GeomVertexWriter, GeomTriangles, GeomNode, NodePath, Point3, GeomPoints, TextNode
from direct.gui.OnscreenText import OnscreenText
from graphics import start_new_line, draw_line, player_win
from object_loader import loadObject
from bonus import test_bonus

from direct.particles.ParticleEffect import ParticleEffect

def init_player(self, left_btn, right_btn, player_number ,pos=(0,0,0), heading=0):
    color = (configs.COLORS_MAP[player_number][0])

    nodePath = loadObject()
    nodePath.setPos(pos)
    nodePath.setScale(configs.SCALE*0.004)
    nodePath.setColor(color)

    p = ParticleEffect()
    p.loadConfig('textures/flare.ptf')
    p.start(parent = nodePath, renderParent = render)
    p0 = p.getParticlesList()[0]
    p0.emitter.setRadiateOrigin(Point3(0.05*cos(heading* pi/180), 0.0, 0.05*sin(heading* pi/180)))
    p.setPos(0,-1,0)
    # p.setBin("unsorted", 0)
    # p.setDepthTest(False)
    p.setTwoSided(True)

    text= TextNode('text') 
    text.setText(str("%s" % player_number))
    text.setTextColor(color)
    text.setAlign(TextNode.ACenter)
    # text.font = self.font
    text3d = NodePath(text) 
    text3d.setTwoSided(True)
    text3d.setPos(nodePath, -1,-3,-4)
    text3d.reparentTo(render)
    circle = loadObject(tex='circle.png')
    circle.reparentTo(render)
    circle.setPos(nodePath, 0,-2,0)
    text3d.setScale(0.13)
    circle.setScale(0.09)
    text3d.setColorScale(color)
    circle.setColorScale(color)


    new_line, line_vertex, line_node = start_new_line(self, pos[0], pos[2], color)
    line_id = configs.ENTITY_ID
    configs.ENTITIES[configs.ENTITY_ID] = {'CATEGORY':'line', 'GEOM':new_line, 'VERTEX':line_vertex, "NODE": line_node}
    configs.ENTITY_ID += 1
    speed = configs.FORWARD_SPEED
    right_angle = configs.FORCE_RIGHT_ANGLE_TURN
    # print left_btn
    # print right_btn
    self.accept(("%s" % left_btn),     player_controls, [configs.ENTITY_ID, 'TURN_LEFT', 1])
    self.accept(("%s-up" % left_btn),  player_controls, [configs.ENTITY_ID, 'TURN_LEFT', 0])
    self.accept(("%s" % right_btn),     player_controls, [configs.ENTITY_ID, 'TURN_RIGHT', 1])
    self.accept(("%s-up" % right_btn),  player_controls, [configs.ENTITY_ID, 'TURN_RIGHT', 0])

    configs.ENTITIES[configs.ENTITY_ID] = {'CATEGORY':'player','ALIVE':True, 'NODE':nodePath,'PARTICLE_PARENT':p, 'PARTICLE':p0, 
        'HEADING':heading, 'CURRENT_LINE':line_id, 'TICKNESS':configs.SCALE, 'TURN_LEFT':0, 'TURN_RIGHT':0, 'COLOR':color, 
        'PLAYER_ID':text3d, 'CIRCLE_NODE':circle, 'LEFT_ARMED':True, 'RIGHT_ARMED':True, 'PLAYER_NUMBER': player_number, 'SPEED':speed,
        'RIGHT_ANGLE_TURN':right_angle }
    configs.ENTITY_ID += 1
    
def player_controls(entity_id, which_button, value):
    if value == 0:
        if which_button == 'TURN_RIGHT':
            configs.ENTITIES[entity_id]['RIGHT_ARMED'] = True
        if which_button == 'TURN_LEFT':
            configs.ENTITIES[entity_id]['LEFT_ARMED'] = True
    configs.ENTITIES[entity_id][which_button] = value

def update_players(self, dt):
    if configs.GAME_ONGOING == 0:
        return
    players_alive = 0
    average_x_pos = 0.0
    average_y_pos = 0.0
    min_x_pos = 0
    max_x_pos = 0
    min_y_pos = 0
    max_y_pos = 0
    for entity_id, entity in configs.ENTITIES.items():
        if entity['CATEGORY'] == 'player':
            if configs.ARDUINO_MODE == True:
                value  = configs.ARDUINO_BUTTONS_MAP[entity['PLAYER_NUMBER']][0]
                which_button = 'TURN_LEFT'
                if value == False:
                    entity['LEFT_ARMED'] = True
                entity[which_button] = value
                value  = configs.ARDUINO_BUTTONS_MAP[entity['PLAYER_NUMBER']][1]
                which_button = 'TURN_RIGHT'
                if value == False:
                    entity['RIGHT_ARMED'] = True
                entity[which_button] = value
            if entity['ALIVE'] == False:
                entity['PARTICLE_PARENT'].disable()
                entity['PARTICLE_PARENT'].reset()
                entity['NODE'].detachNode()
                continue
            players_alive += 1
            if entity['RIGHT_ANGLE_TURN'] == True:
                test_heading = square_heading(entity['HEADING']) 
                entity['HEADING'] = test_heading
                # print test_heading

            if entity['RIGHT_ANGLE_TURN'] == True:
                if entity['TURN_LEFT'] and entity['LEFT_ARMED'] == True:
                    entity["HEADING"] += 90
                    entity['LEFT_ARMED'] = False
                if entity['TURN_RIGHT'] and entity['RIGHT_ARMED'] == True:
                    entity["HEADING"] -= 90 
                    entity['RIGHT_ARMED'] = False 
            else:
                if entity['TURN_LEFT']:
                    entity["HEADING"] += configs.TURN_SPEED *dt*50
                if entity['TURN_RIGHT']:
                    entity["HEADING"] -= configs.TURN_SPEED *dt*50
                
            pos = entity["NODE"].getPos()
            heading = entity["HEADING"]
            last_pos_x = pos.x
            last_pos_y = pos.z
            new_pos_x = last_pos_x + entity['SPEED'] *dt*50 * cos(heading* pi/180)
            new_pos_y = last_pos_y + entity['SPEED'] *dt*50 * sin(heading* pi/180)

            new_pos_x, new_pos_y = test_boundaries(self, entity_id, new_pos_x, new_pos_y)
            test_bonus(self, entity_id)

            dot_size = entity["TICKNESS"]
            entity["NODE"].setPos(new_pos_x,0,new_pos_y)
            entity["NODE"].setScale(dot_size*0.004)
            entity["PARTICLE"].emitter.setRadiateOrigin(Point3(0.05*cos(heading* pi/180), 0.0, 0.05*sin(heading* pi/180)))

            average_x_pos += new_pos_x
            average_y_pos += new_pos_y
            if min_y_pos > new_pos_y:
                min_y_pos = new_pos_y
            if max_y_pos < new_pos_y:
                max_y_pos = new_pos_y
            if min_x_pos > new_pos_x:
                min_x_pos = new_pos_x
            if max_x_pos < new_pos_x:
                max_x_pos = new_pos_x

            time = globalClock.getFrameTime()
            # print time
            if configs.LINE_GAP == True:
                if time % 5 < 4.5:
                    if entity["CURRENT_LINE"] == None:
                        new_line, line_vertex, line_node = start_new_line(self, new_pos_x, new_pos_y, entity['COLOR'])
                        line_id = configs.ENTITY_ID
                        configs.ENTITIES[configs.ENTITY_ID] = {'CATEGORY':'line', 'GEOM':new_line, 'VERTEX':line_vertex, 'NODE': line_node}
                        configs.ENTITY_ID += 1
                        entity["CURRENT_LINE"] = line_id
                        draw_line(entity_id, start=True)
                    create_dots(entity_id, new_pos_x, new_pos_y, dot_size)
                    draw_line(entity_id)
                else:
                    if entity["CURRENT_LINE"] != None:
                        draw_line(entity_id, end=True)
                        entity["CURRENT_LINE"] = None
            else:
                if entity["CURRENT_LINE"] == None:
                    new_line, line_vertex, line_node = start_new_line(self, new_pos_x, new_pos_y, entity['COLOR'])
                    line_id = configs.ENTITY_ID
                    configs.ENTITIES[configs.ENTITY_ID] = {'CATEGORY':'line', 'GEOM':new_line, 'VERTEX':line_vertex, 'NODE': line_node}
                    configs.ENTITY_ID += 1
                    entity["CURRENT_LINE"] = line_id
                    draw_line(entity_id, start=True)
                create_dots(entity_id, new_pos_x, new_pos_y, dot_size)
                draw_line(entity_id)
    if players_alive <= 1:
        player_win(self)

    # if players_alive > 0:
    #     average_x_pos = average_x_pos / players_alive
    #     average_y_pos = average_y_pos / players_alive
    #     center_x = (min_x_pos + max_x_pos)/2
    #     center_y = (min_y_pos + max_y_pos)/2
    #     distance = pow(pow((min_x_pos - min_y_pos),2) + pow((min_x_pos - min_x_pos),2), 0.5)

    #     self.cameraPivot.setHpr(average_x_pos*5,average_y_pos*5,0)
    #     self.cameraPivot.setPos(center_x,0,center_y)
    #     self.cameraArm.setPos(0,(-distance*2)-3,0)


def square_heading(heading):
    # print heading
    while heading < 0:
        heading += 360
    while heading > 360:
        heading -= 360
    if heading >= 45 and heading <= 135:
        return 90
    elif heading >= 135 and heading <= 225:
        return 180
    elif heading >= 225 and heading <= 315:
        return 270
    elif heading >= 315 or heading <= 45:
        return 0

def test_collisions(self, task):
    return task.again

def create_dots(entity_id,  new_pos_x, new_pos_y, size):
    time = globalClock.getFrameTime()
    pos_x = int(((new_pos_x + 1.8)/2) * 1280/1.8) + 50
    pos_y = int(((new_pos_y + 1)/2) * 720/1) + 50

    for i in range((pos_x - size),(pos_x + size)):
        for j in range((pos_y - size),(pos_y + size)):
            if configs.COLLISION_MAP[i][j][0] == 0:
                configs.COLLISION_MAP[i][j][0] = 1
                configs.COLLISION_MAP[i][j][1] = entity_id
                configs.COLLISION_MAP[i][j][2] = time
            else:
                if configs.COLLISION_MAP[i][j][1] == entity_id and ((time - configs.COLLISION_MAP[i][j][2]) < 1): 
                    # print (configs.COLLISION_MAP[i][j][2])
                    continue
                else:
                    configs.ENTITIES[entity_id]['ALIVE'] = False

def test_boundaries(self, entity_id, new_pos_x, new_pos_y):
    entity = configs.ENTITIES[entity_id]
    teleport = False
    if new_pos_x > 1.8:
        if configs.BORDER == True:
            entity['ALIVE'] = False
        else:
            new_pos_x = -1.8
            teleport = True
    if new_pos_x < -1.8:
        if configs.BORDER == True:
            entity['ALIVE'] = False
        else:
            new_pos_x = 1.8
            teleport = True
    if new_pos_y > 1:
        if configs.BORDER == True:
            entity['ALIVE'] = False
        else:
            new_pos_y = -1
            teleport = True
    if new_pos_y < -1:
        if configs.BORDER == True:
            entity['ALIVE'] = False
        else:
            new_pos_y = 1
            teleport = True
    if teleport == True:
        if entity["CURRENT_LINE"] != None:
            draw_line(entity_id, end=True)
            entity["CURRENT_LINE"] = None
            new_line, line_vertex, line_node = start_new_line(self, new_pos_x, new_pos_y, entity['COLOR'])
            line_id = configs.ENTITY_ID
            configs.ENTITIES[configs.ENTITY_ID] = {'CATEGORY':'line', 'GEOM':new_line, 'VERTEX':line_vertex, 'NODE':line_node}
            configs.ENTITY_ID += 1
            entity["CURRENT_LINE"] = line_id

    return new_pos_x, new_pos_y
