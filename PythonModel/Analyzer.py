#!/usr/bin/python

import game_models
import game_visualization

import sys
import pandas
import os
from sklearn import linear_model
import numpy as np
import multiprocessing
import math

def prepare_names(game_model):
    res = []
    for it in game_model.points:
        res.append(game_model.points[it].id+"-p")
        res.append(game_model.points[it].id+"-s")
        res.append(game_model.points[it].id+"-t")

    return res

def get_points_of_interest(game_model):
    points_of_interest_s = game_model.SKIPS \
                         + game_model.REPEATS

    points_of_interest_p = [item for sublist in game_model.FORKS.values() for item in sublist]

    points_of_interest_t = list(game_model.TRANSITIONS.keys())

    return [p+"-s" for p in points_of_interest_s] + [p+"-p" for p in points_of_interest_p] + [p+"-t" for p in points_of_interest_t]


def game_to_df(game):
    feature_names = prepare_names(game.model)
    line = {}

    for it in feature_names:
        line[it] = 0

    for it in game.passLog:
        line[it.id+"-p"] += 1

    for it in game.stopLog:
        line[it.id+"-s"] += 1

    for it in game.transitionLog:
        line[it.id+"-t"] += 1

    line["turns"] = game.turn

    return pandas.DataFrame([line])

def generate_games_parallel(games_qty, game_model_filename, pid_from, pid_to, num_workers=4):
    pool = multiprocessing.Pool(processes=num_workers)
    params = {"games_qty":math.ceil(games_qty / num_workers), "game_model_filename":game_model_filename, "pid_from":pid_from, "pid_to":pid_to}
    frames = pool.map(generate_games, [params]*num_workers)
    res = pandas.DataFrame()
    for df in frames:
        res = res.append(df)
    return res


def generate_games(params):
    gm = game_models.GameModel.read(params["game_model_filename"])
    game = game_models.Game(gm)
    df = pandas.DataFrame()

    for i in range(params["games_qty"]):
        game.play(pidFrom=params["pid_from"], pidTo=params["pid_to"])
        df = df.append(game_to_df(game))
        if i % 100 == 0:
            sys.stdout.write("\r%d%%" % (i*100 / params["games_qty"]))
            sys.stdout.flush()

    return df


def get_data(game_model_filename, filename=None, iterations=1000, pid_from="p0", pid_to="p0"):
    if not filename:
        return generate_games_parallel(iterations, game_model_filename, pid_from, pid_to)

    if os.path.isfile(filename):
        return pandas.read_csv(filename, sep='\t')
    else:
        df = generate_games_parallel(iterations, game_model_filename, pid_from, pid_to)
        df.to_csv(filename, sep='\t')
        return df

def build_regression(game_model, factors_turns):
    lr = linear_model.Ridge()

    selected_feature_names = np.array(get_points_of_interest(game_model))
    print( selected_feature_names)

    df1 = factors_turns[selected_feature_names]

    feature_names = list(factors_turns.columns.values)
    feature_names.remove("turns")
    feature_names = list(filter(lambda x: "-t" not in x, feature_names))
    feature_names = np.array(feature_names)
    # print(df["turns"])
    lr.fit(df1, factors_turns["turns"])
    coefs = lr.coef_
    argsort = np.argsort(np.abs(coefs))[::-1]
    cf = pandas.DataFrame(np.vstack((selected_feature_names[argsort],coefs[argsort])).T)

    pandas.set_option('display.max_rows', 500)

    print(cf)


def calc_percentiles(factors_turns):
    try:
        return np.percentile(factors_turns["turns"], list(range(5,100,5)), interpolation="higher")
    except:
        return None

def calc_averages(game_model, factors_turns):
    ap = lambda x: game_model.getAnnotatedPid(x)

    for it in game_model.FORKS:
        print(ap(it))
        forks = game_model.FORKS[it]
        fork_stat = dict( (pid, calc_subset_stats(factors_turns[factors_turns[pid+"-p"] > 0]) ) for pid in forks)
        for key in fork_stat:
            print(ap(key), fork_stat[key])


def calc_subset_stats(subset):
    return {
            "mean":np.mean(subset["turns"]),
            "percentiles":calc_percentiles(subset),
           }

def main():
    #(sys.argv[2] if len(sys.argv) > 2 else None)

    # model_name = "model-initial"
    model_name = "model1"
    iterations = 2000
    # pid_from=(sys.argv[3] if len(sys.argv) > 3 else "p0")
    # pid_to=(sys.argv[4] if len(sys.argv) > 4 else "p0")
    pid_from="p70"
    pid_to="p177"

    filename = "_".join([model_name, pid_from, pid_to, str(iterations)])+".tsv"

    md = game_models.GameModel.read(model_name+".dat")

    gp = game_visualization.GamePlotter()
    gp.plot_model(md)

    df = get_data(game_model_filename=model_name+".dat", filename=filename, iterations=iterations, pid_from=pid_from, pid_to=pid_to)
    # build_regression(game_model=md, factors_turns=df)
    calc_averages(game_model=md, factors_turns=df)



    # print(str(game.turn) + "\t" + "\t".join([("*" if p in game.log else "")+p.dump() for p in game.transitLog]))

if __name__=="__main__":
    main()