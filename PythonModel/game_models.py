from enum import Enum
import random


class PointType(Enum):
    none = 0
    capital = 1
    city = 2
    skip = 3
    repeat = 4


class Point:
    id = None
    connections = []
    transition = None
    type = PointType.none

    def __init__(self, pointId):
        self.id = pointId
        self.connections = []

    def addConnection(self, targetPoint):
        if targetPoint not in self.connections:
            self.connections.append(targetPoint)

    def setTransition(self, targetPoint):
        self.transition = targetPoint;

    def getConnections(self):
        return self.connections

    def __eq__(self, other):
        if self.id != other.id:
            return False

        if self.type != other.type:
            return False

        if self.transition != other.transition:
            return False

        if len(self.connections) != len(other.connections):
            return False

        for it in self.connections:
            if it not in other.connections:
                return False

        return True

    def __str__(self):
        return "<"+self.id+">"

    def dump(self):
        output = "!"+self.id+"-"+str(self.type)

        output += "["
        for cpt in self.connections:
            output += ">"+cpt.id
        output += "]"

        if self.transition is not None:
            output += ">>"+self.transition.id

        return output


class GameModel:
    points = {}
    turnNumber = 0

    #END_POINTS = ["p236", "p264", "p289", "p298", "p308"]
    #PARTS = [0, 237, 265, 290, 299]

    POINTS_QTY = 309
    SKIPS = [
        "p9", "p10", #Гренландия
        "p25", #Бизоны
        "p35", #Вегас
        "p46", #Панамский канал
        "p49", "p50", #Колумбия
        "p73", "p75", "p77", "p79", #Антарктида
        "p106", "p107", "p108", #Сахара
        "p130", "p131", #Непал
        "p199", "p203", "p207" #Дальний Восток
        "p237", #Ла-Манш
        "p273", #Акула
        "p294", "p295", "p296", "p297", "p298", #Австралия
        "p301", "p303", "p305" #Север
    ]
    REPEATS = [
        "p28", #США - автобус
        "p80", #Антарктида
        "p116", #Багдад
        "p161", #Канберра
        "p171", #Воздушный шар
        "p205", #Газ66
        "p213", #Сибирь
        "p222", #Урал
        "p233", #Греция
        "p244", #Гаити
        "p253", #Кораблик
    ]
    CITIES = [
        "p5", #Рейкьявик
        "p18", #Квебек
        "p20", #Вашингтон
        "p33", #Сан-Франциско
        "p36", #Лос-Анжелес
        "p42", #Мехико
        "p56", #Бразилиа
        "p61", #Буэнос-Айрес
        "p95", #Кейптаун
        "p110", #Каир
        "p111", #Тель-Авив
        "p115", #Тегеран
        "p118", #Дубай
        "p123", #Бангалор
        "p129", #Дели
        "p136", #Бангкок
        "p141", #Джакарта
        "p160", #Мельбурн
        "p162", #Сидней
        "p176", #Манила
        "p192", #Владивосток
        "p211", #Иркутск
        "p217", #Новосибирск
        "p223", #Екатеринбург
        "p234", #Рим
        #Ветка 2
        "p241", #Гаванна
    ]
    CAPITALS = [
        "p0", #Лондон
        "p19", #Нью-Йорк
        "p183", #Токио
        "p189", #Пекин
        "p228", #Москва
        "p236", #Париж
    ]
    FORKS = {
        "p42":["p43","p238"], #Южная Америка
        "p95":["p96","p265"], #Африка
        "p141":["p142","p290"], #Австралия
        "p141":["p142","p290"], #Австралия
        "p217":["p218","p299"], #Россия
    }

    JOINTS = {
        "p237":"p0", #Главный цикл
        "p264":"p56", #Южная Америка
        "p289":"p110", #Африка
        "p298":"p161", #Австралия
        "p308":"p228", #Россия
    }

    TRANSITIONS = {
        "p1":"p14", #Ирландия - Канада
        "p48":"p42", #Колумбия
        "p84":"p71", #Антарктида
        "p109":"p95", #Мумия
        "p126":"p123", #Тигр
        "p137":"p176", #Облёт Австралии
        "p150":"p157", #Вдоль Австралии
        "p182":"p135", #Якудза
        "p193":"p211", #Владивосток - Иркутск
        "p212":"p217", #Иркутск - Новосибирск
        "p214":"p299", #Медведь
        "p218":"p223", #Новосибирск - Екатеринбург
        "p224":"p228", #Екатеринбург - Москва
        "p260":"p269", #Атлантика
        "p278":"p256", #Мамонтёнок
    }

    ANNOTATIONS = {}

    def __init__(self):
        self.fill()

    def fill(self):
        self.createPoints()
        self.setTransitions()
        self.setConnections()

    def createPoints(self):
        self.points.clear()

        for i in range(self.POINTS_QTY):
            pid = "p"+str(i)
            point = Point(pid)

            if pid in self.SKIPS:
                point.type = PointType.skip
            elif pid in self.REPEATS:
                point.type = PointType.repeat
            elif pid in self.CAPITALS:
                point.type = PointType.capital
            elif pid in self.CITIES:
                point.type = PointType.city

            self.points[pid] = point

    def setConnections(self):
        for pid in self.points:
            if pid in self.FORKS.keys():
                for p in self.FORKS[pid]:
                    self.points[pid].addConnection(self.points[p])

            elif pid in self.JOINTS.keys():
                self.points[pid].addConnection(self.points[self.JOINTS[pid]])

            else:
                self.points[pid].addConnection(self.points[self.intToPid(self.pidToInt(pid) + 1)])

    def setTransitions(self):
        for srcPid in self.TRANSITIONS:
            self.points[srcPid].setTransition(self.points[self.TRANSITIONS[srcPid]])

    def getStartPosition(self):
        return self.points[self.CAPITALS[0]]

    def getAnnotatedPid(self, pid):
        return pid+"("+self.ANNOTATIONS[pid]+")" if pid in self.ANNOTATIONS else pid

    def getAnnotation(self, pid):
        return self.ANNOTATIONS[pid] if pid in self.ANNOTATIONS else None

    @staticmethod
    def intToPid(intNum):
        return "p"+str(intNum)

    @staticmethod
    def nextPoint(pid):
        return GameModel.intToPid(GameModel.pidToInt(pid) + 1)

    @staticmethod
    def pidToInt(pid):
        return int(pid[1:])

    def __str__(self):
        return "\t".join([self.points[it].dump() for it in self.points])

    def clear(self):
        self.points.clear()
        self.CITIES.clear()
        self.CAPITALS.clear()
        self.FORKS.clear()
        self.JOINTS.clear()
        self.REPEATS.clear()
        self.SKIPS.clear()
        self.TRANSITIONS.clear()
        self.ANNOTATIONS.clear()

    def extract_paths(self):
        paths = [[]]
        stack = []
        marked = []
        point = self.points['p0']

        stack.append(point)

        while len(stack) > 0:
            point = stack.pop()

            if point in marked:
                paths.append([])
                continue
            marked.append(point)
            paths[-1].append(point)

            for connected in point.connections:
                stack.append(connected)

        return paths

    @staticmethod
    def read(filename):
        file = open(filename)
        counter = 0
        model = GameModel()
        model.clear()

        tmpTransitions = {}
        tmpForks = {}
        tmpPaths = {}

        for line in file:
            tmpArray = line.strip().split("|")
            pathId = int(tmpArray[0])
            pathNodes = tmpArray[1].split(";")
            tmpPaths[pathId] = {"start":GameModel.intToPid(counter)}
            for node in pathNodes:

                parts = node.split("-")
                pointType = parts[0][0]
                pointCount = int(parts[0][1:])

                if pointType not in "ncCsr":
                    raise SyntaxError("Undefined point type: %s at point %s"% (pointType, counter))

                pid = None
                for i in range (pointCount):
                    pid = GameModel.intToPid(counter)
                    if pointType == "c":
                        model.CITIES.append(pid)
                    elif pointType == "C":
                        model.CAPITALS.append(pid)
                    elif pointType == "s":
                        model.SKIPS.append(pid)
                    elif pointType == "r":
                        model.REPEATS.append(pid)
                    counter += 1;

                for part in parts[1:]:
                    key = part[0]
                    value = part[1:]

                    if key in "TtFf":
                        value = int(value)

                    if key in "Tt":
                        if value not in tmpTransitions:
                            tmpTransitions[value] = {}
                        if key=="T":
                            tmpTransitions[value]["src"] = pid
                        elif key == "t":
                            tmpTransitions[value]["dest"] = pid
                    if key in "Ff":
                        if value not in tmpForks:
                            tmpForks[value] = {}
                        if key=="F":
                            tmpForks[value]["src"] = pid
                        elif key == "f":
                            tmpForks[value]["dest"] = pid
                    if key in "a":
                        model.ANNOTATIONS[pid]=value

            tmpPaths[pathId]["end"] = GameModel.intToPid(counter-1)

        model.POINTS_QTY = counter;

        for it in tmpTransitions:
            model.TRANSITIONS[tmpTransitions[it]["src"]] = tmpTransitions[it]["dest"]

        for it in tmpForks:
            if it!=0: #dirty hack
                model.FORKS[tmpForks[it]["src"]] = [tmpPaths[it]["start"], GameModel.nextPoint(tmpForks[it]["src"])]
            model.JOINTS[tmpPaths[it]["end"]] = tmpForks[it]["dest"]

        model.fill()
        return model


class Game:

    model = None
    position = None
    endPosition = None
    turn = 0
    isGameOver = False
    stopLog = []
    passLog = []
    transitionLog = []
    turnEndLog = []

    def __init__(self, model):
        self.model = model

    def play(self, pidFrom=None, pidTo=None):
        self.isGameOver = False

        self.position = self.model.points[pidFrom] if self.model.points[pidFrom] is not None else self.model.getStartPosition()
        self.endPosition = self.model.points[pidTo] if self.model.points[pidTo] is not None else self.position
        self.turn = 0
        self.stopLog = [self.position]
        self.passLog = [self.position]
        self.transitionLog = []
        self.turnEndLog = []

        while not self.isGameOver:
            self.makeTurn()

    def rollDice(self):
        return random.randint(1,6)

    def makeTurn(self):
        self.position = self.getNextPosition(self.rollDice())
        self.stopLog.append(self.position)

        if self.position.type == PointType.skip:
            self.turn += 2
            self.turnEndLog.append(self.position)
            self.turnEndLog.append(self.position)
        elif self.position.type != PointType.repeat:
            self.turn += 1
            self.turnEndLog.append(self.position)

    def getNextPosition(self, roll):
        currentPoint = self.position
        for i in range (roll):
            connections = currentPoint.getConnections()
            currentPoint = random.choice(connections)

            if currentPoint == self.endPosition:
                self.isGameOver = True
                return currentPoint

            self.passLog.append(currentPoint)

        while currentPoint.transition is not None:
            self.transitionLog.append(currentPoint)
            currentPoint = currentPoint.transition
            self.passLog.append(currentPoint)

        return currentPoint
