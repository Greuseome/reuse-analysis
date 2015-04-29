import os
import glob
import pandas as pd

eval_dir = os.path.join('/scratch',
                        'cluster',
                        'mhollen',
                        'single-source',
                        'evaluations')

games = ['breakout',
'pong',
'space_invaders',
'asterix',
'freeway',
'boxing',
'seaquest',
'bowling'
]

fitness_history = {}
#fitness_history = pd.DataFrame(columns=range(200))
def grab_fitness_history(game, transfer=None):
    g = game if transfer is None else '{}-using-{}'.format(game,transfer)
    fpath = os.path.join(eval_dir, g, 'run-*','fitness.history')
    files = glob.glob(fpath)
    for i,f in enumerate(files):
        df = pd.read_csv(f,
                         sep=',',
                         index_col=False,
                         skiprows=0,
                         header=None)
        fitness_history[(game,transfer,i)] = df.dropna(axis=1)


for game in games:
    # scratch
    grab_fitness_history(game, None)
    # random
    grab_fitness_history(game, 'random-{}'.format(game))
    # transfers
    for tx in games:
        if tx == game: continue
        grab_fitness_history(game, tx)

index = pd.MultiIndex.from_tuples(fitness_history.keys(),
                                 names = ['game','tx','run'])
df = pd.DataFrame([x.values[0] for x in fitness_history.values()],
                  index = index,
                  columns = range(200))
df = df.sort_index()
df.to_pickle('single-source-results.pkl')
df.to_csv('single-source-results.csv')
