from panda3d.core import GeomVertexData, GeomVertexWriter, GeomTristrips, GeomNode
from panda3d.core import NodePath, Point3, LineSegs, NodePath, GeomLines, Geom, GeomVertexFormat
from direct.gui.DirectGui import OnscreenText
from math import cos, sin, pi 
import configs

def draw_line(entity_id, end=False, start=False):
    entity = configs.ENTITIES[entity_id]
    pos = entity["NODE"].getPos()
    heading = entity['HEADING']
    tickness = entity['TICKNESS']
    if end == True:
        pos_x = pos.x + (0.002 * cos(heading* pi/180))
        pos_z = pos.z + (0.002 * sin(heading* pi/180))
    elif start == True:
        pos_x = pos.x - (0.002 * cos(heading* pi/180))
        pos_z = pos.z - (0.002 * sin(heading* pi/180))
    else:
        pos_x = pos.x
        pos_z = pos.z
    left_vertice_x = pos_x + (tickness*0.0028) * cos((heading+90)* pi/180)
    left_vertice_y = pos_z + (tickness*0.0028) * sin((heading+90)* pi/180)
    right_vertice_x = pos_x + (tickness*0.0028) * cos((heading-90)* pi/180)
    right_vertice_y = pos_z + (tickness*0.0028) * sin((heading-90)* pi/180)
    line_entity = configs.ENTITIES[entity['CURRENT_LINE']]
    point1 = Point3(left_vertice_x, 0.0 , left_vertice_y)
    point2 = Point3(right_vertice_x, 0.0 , right_vertice_y)
    current_line = line_entity['GEOM']
    vertex_data = line_entity['VERTEX']
    
    pos_writer = GeomVertexWriter(vertex_data, "vertex")
    rows = vertex_data.get_num_rows()
    pos_writer.set_row(rows)
    pos_writer.add_data3f(point2)
    pos_writer.add_data3f(point1)
    current_line.add_vertices(rows - 1, rows)

def start_new_line(self, pos_x, pos_y, color):
    new_line = GeomTristrips(Geom.UH_static)
    vertex_format = GeomVertexFormat.get_v3()
    vertex_data = GeomVertexData("path_data", vertex_format, Geom.UH_static)
    pos_writer = GeomVertexWriter(vertex_data, "vertex")
    pos_writer.add_data3f(pos_x, 0.0, pos_y)
    geom = Geom(vertex_data)
    geom.add_primitive(new_line)
    geom_node = GeomNode("path")
    geom_node.add_geom(geom)
    path = self.render.attach_new_node(geom_node)
    path.set_color(1., 1., 1.)
    path.setColor(color)
    # path.setBin("unsorted", 0)
    # path.setDepthTest(False)
    path.setTwoSided(True)
    return new_line, vertex_data, path

def player_win(self):
    if configs.GAME_WON == False:
        winner = ''
        configs.GAME_WON = True
        # sound = base.loader.loadSfx("sounds/endgame.ogg")
        # sound.setVolume(0.5)
        # sound.play()
        for entity_id, entity in configs.ENTITIES.items():
            if entity['CATEGORY'] == 'player':
                if entity['ALIVE'] == True:
                    winner = entity['PLAYER_NUMBER']  

        self.winner = OnscreenText(text="Player %s win" % winner, scale=0.2, pos=(0, 0),
                        fg=(1, 1, 1, 0.8), shadow=(0, 0, 0, 0.5))

        task = taskMgr.doMethodLater(5, self.reset_game, 'reset game', extraArgs=[self])
