#!c:\anaconda3\python3

import game_models
import math
from graphviz import Digraph

class GamePlotter:

    TYPE_COLORS = {
        game_models.PointType.capital:"red",
        game_models.PointType.city:"yellow",
        game_models.PointType.repeat:"green",
        game_models.PointType.skip:"gray",
        game_models.PointType.none:"white"
    }

    def plot_model(self, game_model : game_models.GameModel, radius=200):
        paths = game_model.extract_paths()

        coords = {}
        path_length = len(paths[0])
        for pos in range(path_length):
            x = radius * math.cos(pos*2*math.pi / path_length )
            y = radius * math.sin(pos*2*math.pi / path_length )
            coords[paths[0][pos].id] = {"x":x, "y":y}

        graph = Digraph(format='svg', engine="neato")

        for pid in game_model.points:
            pos = "%f,%f" % (coords[pid]["x"], coords[pid]["y"]) if pid in coords else None
            fillcolor = self.TYPE_COLORS[game_model.points[pid].type]

            graph.node(pid, pos=pos, style="filled", fillcolor=fillcolor, tooltip=game_model.getAnnotatedPid(pid))

        for pid in game_model.points:
            for connection in game_model.points[pid].connections:
                graph.edge(pid, connection.id)

        for pid in game_model.points:
            transition = game_model.points[pid].transition
            if transition is None:
                continue
            target_pid = game_model.points[pid].transition.id
            color = "green" if game_models.GameModel.pidToInt(pid) < game_models.GameModel.pidToInt(target_pid) else "red"
            graph.edge(pid, target_pid, color=color)

        graph.render('test')