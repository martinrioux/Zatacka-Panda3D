
from panda3d.core import Vec3
import random
from object_loader import loadObject
import configs
import copy
from math import sin

def init_bonus_tasks(self):
    taskMgr.add(flipScreen, 'flipScreen', extraArgs = [self], appendTask=True)
    taskMgr.add(cleanLine, 'cleanLine', extraArgs = [self], appendTask=True)
    taskMgr.add(removeBorder, 'removeBorder', extraArgs = [self], appendTask=True)

def spawn_bonus(self, task):
    time = globalClock.getFrameTime()
    if configs.NEXT_BONUS_TIME <= time:
        if configs.GAME_WON == True:
            return task.done
        if configs.FORCE_RIGHT_ANGLE_TURN == True:
            which_bonus = random.randint(1, 7)
        else:
            which_bonus = random.randint(0, 7)
        position = Vec3(random.uniform(-1.8, 1.8), random.uniform(-1, 1), 0)
        bonus = loadObject("bonus_%s.png" % which_bonus, scale=0.05, pos=position)
        bonus.setY(-0.01)
        me = random.randint(0,1)
        if me == 1:
            bonus.setColor(0,0,1,1)
        else:
            bonus.setColor(1,0,0,1)
        if which_bonus == 1 or  which_bonus == 2 or  which_bonus == 5:
            bonus.setColor(0,1,0,1)
        configs.ENTITIES[configs.ENTITY_ID] = {'CATEGORY':'bonus', 'NODE':bonus, "BONUS_ID":which_bonus, 'ME':me}
        configs.ENTITY_ID += 1
        
        delay = random.randint(3, 10)
        configs.NEXT_BONUS_TIME = time + delay
    return task.cont

def test_bonus(self, player_id):
    player = configs.ENTITIES[player_id]
    for bonus_id, bonus in configs.ENTITIES.items():
        if bonus['CATEGORY'] == 'bonus':
            if ((player['NODE'].getPos() - bonus['NODE'].getPos()).lengthSquared() <
                    (((player['NODE'].getScale().getX() + bonus['NODE'].getScale().getX())
                      * 1) ** 2)):
                bonus['NODE'].removeNode()
                del(configs.ENTITIES[bonus_id])

                time = globalClock.getFrameTime()

                if bonus['BONUS_ID'] == 1 or bonus['BONUS_ID'] == 2 or bonus['BONUS_ID'] == 5:
                    configs.BONUS_START_TIME[bonus['BONUS_ID']] = time

                else:
                    taskMgr.add(BONUS_HANDLER[bonus['BONUS_ID']], 'bonus', extraArgs = [self, player_id, bonus['ME'], 1], appendTask=True)
                    # taskMgr.add(speedUp, 'speedUp', extraArgs = [self, bonus['player_id'], bonus['WHO']], appendTask=True)
                    # taskMgr.add(speedDown, 'speedDown', extraArgs = [self, bonus['player_id'], bonus['WHO']], appendTask=True)
                    # taskMgr.add(increase_scale, 'increase_scale', extraArgs = [self, bonus['player_id'], bonus['WHO']], appendTask=True)
                    # taskMgr.add(decrease_scale, 'decrease_scale', extraArgs = [self, bonus['player_id'], bonus['WHO']], appendTask=True)
                    # taskMgr.add(rightAngle, 'rightAngle', extraArgs = [self, bonus['player_id'], bonus['WHO']], appendTask=True)


# GLOBAL BONUS
def flipScreen(self, task):
    time = globalClock.getFrameTime()
    if time - configs.BONUS_START_TIME[1] < 5:
        if configs.SCREEN_FLIPPED == False:
            configs.SCREEN_FLIPPED = True
            position = 180
            interval = self.cameraPivot.hprInterval(0.5, Vec3(position, 0, 0))
            interval.start()
    else:
        if configs.SCREEN_FLIPPED == True:
            configs.SCREEN_FLIPPED = False
            position = 0
            interval = self.cameraPivot.hprInterval(0.5, Vec3(position, 0, 0))
            interval.start()
    return task.cont

def cleanLine(self, task):
    time = globalClock.getFrameTime()
    if time - configs.BONUS_START_TIME[2] < 1:
        configs.BONUS_START_TIME[2] = -100
        for entity_id, entity in configs.ENTITIES.items():
            if entity['CATEGORY'] == 'line':
                entity['NODE'].removeNode()
            if entity['CATEGORY'] == 'player':
                entity['CURRENT_LINE'] = None
        taskMgr.doMethodLater(0.10, clear_collisions, 'Task Stop', extraArgs = [self, 0, 100])
        taskMgr.doMethodLater(0.15, clear_collisions, 'Task Stop', extraArgs = [self, 100, 200])
        taskMgr.doMethodLater(0.20, clear_collisions, 'Task Stop', extraArgs = [self, 200, 300])
        taskMgr.doMethodLater(0.25, clear_collisions, 'Task Stop', extraArgs = [self, 300, 400])
        taskMgr.doMethodLater(0.30, clear_collisions, 'Task Stop', extraArgs = [self, 400, 500])
        taskMgr.doMethodLater(0.35, clear_collisions, 'Task Stop', extraArgs = [self, 500, 600])
        taskMgr.doMethodLater(0.40, clear_collisions, 'Task Stop', extraArgs = [self, 600, 700])
        taskMgr.doMethodLater(0.45, clear_collisions, 'Task Stop', extraArgs = [self, 700, 800])
        taskMgr.doMethodLater(0.50, clear_collisions, 'Task Stop', extraArgs = [self, 800, 900])
        taskMgr.doMethodLater(0.55, clear_collisions, 'Task Stop', extraArgs = [self, 900, 1000])
        taskMgr.doMethodLater(0.60, clear_collisions, 'Task Stop', extraArgs = [self, 1000, 1100])
        taskMgr.doMethodLater(0.65, clear_collisions, 'Task Stop', extraArgs = [self, 1100, 1200])
        taskMgr.doMethodLater(0.70, clear_collisions, 'Task Stop', extraArgs = [self, 1200, 1385])
    return task.cont

def clear_collisions(self, start, end):
    for x in range(825):
        for y in range(start,end):
            configs.COLLISION_MAP[y][x] = [0,0,0] 

def removeBorder(self, task):
    time = globalClock.getFrameTime()
    if time - configs.BONUS_START_TIME[5] < 8:
        self.border.setAlphaScale((sin(time*3)*0.5) + 0.2)
        configs.BORDER = False
    elif time - configs.BONUS_START_TIME[5] < 10: 
        self.border.setAlphaScale((sin(time*9)*0.5) + 0.2)
        configs.BORDER = False
    else:
        configs.BORDER = True
        self.border.setAlphaScale(1)
    return task.cont


# PERSONNAL BONUS
def rightAngle(self, player, me, start, task):
    if configs.FORCE_RIGHT_ANGLE_TURN == True:
        return task.done
    if start == 1:
        for entity_id, entity in configs.ENTITIES.items():
            if entity['CATEGORY'] == 'player':
                if (me == 1 and entity_id == player) or (me == 0 and entity_id != player):
                    entity['RIGHT_ANGLE_TURN'] = True
        taskMgr.doMethodLater(10, rightAngle, 'bonus', extraArgs = [self, player, me, 0], appendTask=True)
    else:
        for entity_id, entity in configs.ENTITIES.items():
            if entity['CATEGORY'] == 'player':
                if (me == 1 and entity_id == player) or (me == 0 and entity_id != player):
                    entity['RIGHT_ANGLE_TURN'] = False
    return task.done

def speedUp(self, player, me, start, task):
    if start == 1:
        for entity_id, entity in configs.ENTITIES.items():
            if entity['CATEGORY'] == 'player':
                if (me == 1 and entity_id == player) or (me == 0 and entity_id != player):
                    entity['SPEED'] = configs.DEFAULT_FORWARD_SPEED * 2
        taskMgr.doMethodLater(10, speedUp, 'bonus', extraArgs = [self, player, me, 0], appendTask=True)
    else:
        for entity_id, entity in configs.ENTITIES.items():
            if entity['CATEGORY'] == 'player':
                if (me == 1 and entity_id == player) or (me == 0 and entity_id != player):
                    entity['SPEED'] = configs.DEFAULT_FORWARD_SPEED
    return task.done


def speedDown(self, player, me, start, task):
    if start == 1:
        for entity_id, entity in configs.ENTITIES.items():
            if entity['CATEGORY'] == 'player':
                if (me == 1 and entity_id == player) or (me == 0 and entity_id != player):
                    entity['SPEED'] = configs.DEFAULT_FORWARD_SPEED / 2
        taskMgr.doMethodLater(10, speedDown, 'bonus', extraArgs = [self, player, me, 0], appendTask=True)
    else:
        for entity_id, entity in configs.ENTITIES.items():
            if entity['CATEGORY'] == 'player':
                if (me == 1 and entity_id == player) or (me == 0 and entity_id != player):
                    entity['SPEED'] = configs.DEFAULT_FORWARD_SPEED
    return task.done


def increase_scale(self, player, me, start, task):
    if start == 1:
        for entity_id, entity in configs.ENTITIES.items():
            if entity['CATEGORY'] == 'player':
                if (me == 1 and entity_id == player) or (me == 0 and entity_id != player):
                    entity['TICKNESS'] = configs.SCALE + 2
        taskMgr.doMethodLater(10, increase_scale, 'bonus', extraArgs = [self, player, me, 0], appendTask=True)
    else:
        for entity_id, entity in configs.ENTITIES.items():
            if entity['CATEGORY'] == 'player':
                if (me == 1 and entity_id == player) or (me == 0 and entity_id != player):
                    entity['TICKNESS'] = configs.SCALE
    return task.done

def decrease_scale(self, player, me, start, task):
    if start == 1:
        for entity_id, entity in configs.ENTITIES.items():
            if entity['CATEGORY'] == 'player':
                if (me == 1 and entity_id == player) or (me == 0 and entity_id != player):
                    entity['TICKNESS'] = configs.SCALE - 1
        taskMgr.doMethodLater(10, decrease_scale, 'bonus', extraArgs = [self, player, me, 0], appendTask=True)
    else:
        for entity_id, entity in configs.ENTITIES.items():
            if entity['CATEGORY'] == 'player':
                if (me == 1 and entity_id == player) or (me == 0 and entity_id != player):
                    entity['TICKNESS'] = configs.SCALE
    return task.done


BONUS_HANDLER = { 
        0 : rightAngle, 
        1 : flipScreen,
        2 : cleanLine,
        3 : speedUp,
        4 : speedDown,
        5 : removeBorder,
        6 : increase_scale,
        7 : decrease_scale
    } 