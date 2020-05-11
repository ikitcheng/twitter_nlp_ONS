import pandas as pd
import seaborn as sns


cm = sns.light_palette("green", as_cmap=True)
avg_sen = pd.read_csv("avg_sen.csv")

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import colors


def background_gradient(s, m=None, M=None, cmap='RdYlGn', low=-1, high=1):
    if m is None:
        m = s.min().min()
    if M is None:
        M = s.max().max()
    rng = M - m
    norm = colors.Normalize(m ,M)
    normed = s.apply(lambda x: norm(x.values))
    cm = plt.cm.get_cmap(cmap)
    c = normed.applymap(lambda x: colors.rgb2hex(cm(x)))
    c.to_csv("colours.csv", index=False)
    ret = c.applymap(lambda x: 'background-color: %s' % x)
    return ret

avg_sen.style.apply(background_gradient, axis=None)

colours = pd.read_csv("colours.csv")
colours = colours.rename(columns={'Average Sentiment': 'hex_colour'})
avg_sen['hex_colour'] = colours
avg_sen.to_csv("sentiment_colours.csv", index=False)
