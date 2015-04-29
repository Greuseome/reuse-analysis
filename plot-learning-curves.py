import pandas as pd
import itertools
import matplotlib.pyplot as plt
from numpy import sqrt

plt.style.use('ggplot')

df = pd.read_pickle('single-source-results.pkl').cummax(axis=1)

# remove random sources
for level in [0,1]:
    df.drop([x for x in df.index.levels[level] if 'random' in x], 
            level=level,
            inplace=True)

# make sure they have 200 generations
df  = df[df.notnull().sum(axis=1)==200]

# plot
fig, ax = plt.subplots(2,4)
fig.set_figwidth(8)
fig.set_figheight(4)
axes = list(itertools.chain.from_iterable(ax))
for i,game in enumerate(df.index.levels[0]):
    gdf = df.ix[game]
    cax = axes[i]

    sm = 20
    gdfm = pd.rolling_mean(gdf.mean(), sm, min_periods=2)
    std  = pd.rolling_mean(gdf.std(), sm, min_periods=2)
    err  = pd.rolling_mean(gdf.std()/sqrt(len(gdf)),
                           sm, min_periods=2)
    gdfm.plot(ax=axes[i], color='k')
    cax.fill_between(range(200),
                     gdfm - std,
                     gdfm + std,
                     color = (.3,.3,.3,.5))
    cax.fill_between(range(200),
                     gdfm - err,
                     gdfm + err,
                     color = (.3,.3,.3,.5))
    gamename = game.replace('_',' ')
    cax.set_xlabel(gamename)
    cax.set_xticklabels([])
    cax.set_yticklabels([])
    cax.set_xticks([])
    cax.set_yticks([])

fig.tight_layout()
fig.savefig('learning_curves.pdf')
plt.show()
