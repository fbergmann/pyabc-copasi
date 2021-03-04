from pyabc.visualization import plot_kde_1d
from pyabc import Distribution, RV
from pyabc.populationstrategy import AdaptivePopulationSize
from pyabc import ABCSMC
import numpy as np
from example_basico_model import *


import matplotlib.pyplot as plt

MAX_T = 0.1
true_rate = 2.3
observations = [BasicoModel('./data/abc_example_model1.xml', MAX_T)({"(R1).k1": true_rate}),
                BasicoModel('./data/abc_example_model2.xml', MAX_T)({"(R1).k1": 30}),
                ]

N_TEST_TIMES = 20

t_test_times = np.linspace(0, MAX_T, N_TEST_TIMES)


def distance(x, y):
    xt_ind = np.searchsorted(x["t"], t_test_times) - 1
    yt_ind = np.searchsorted(y["t"], t_test_times) - 1
    error = (np.absolute(x["X"][:, 1][xt_ind]
                         - y["X"][:, 1][yt_ind]).sum()
             / t_test_times.size)
    return error


prior = Distribution(rate=RV("uniform", 0, 100))


abc = ABCSMC([BasicoModel('./data/abc_example_model1.xml', MAX_T),
              BasicoModel('./data/abc_example_model2.xml', MAX_T)],
             [prior, prior],
             distance,
             population_size=AdaptivePopulationSize(500, 0.15))

abc_id = abc.new("sqlite:////tmp/basico_mjp.db", observations[0])

history = abc.run(minimum_epsilon=0.7, max_nr_populations=15)

ax = history.get_model_probabilities().plot.bar()
ax.set_ylabel("Probability")
ax.set_xlabel("Generation")
ax.legend([1, 2], title="Model", ncol=2,
          loc="lower center", bbox_to_anchor=(.5, 1))

plt.savefig('./out/basico_probs.png')


from pyabc.visualization import plot_kde_1d
fig, axes = plt.subplots(2)
fig.set_size_inches((6, 6))
axes = axes.flatten()
axes[0].axvline(true_rate, color="black", linestyle="dotted")
for m, ax in enumerate(axes):
    for t in range(0, history.n_populations, 2):
        df, w = history.get_distribution(m=m, t=t)
        if len(w) > 0:  # Particles in a model might die out
            plot_kde_1d(df, w, "rate", ax=ax, label=f"t={t}",
                        xmin=0, xmax=20 if m == 0 else 100,
                        numx=200)
    ax.set_title(f"Model {m+1}")
axes[0].legend(title="Generation",
          loc="upper left", bbox_to_anchor=(1, 1));

fig.tight_layout()
plt.savefig('./out/basico_distrib.png')


populations = history.get_all_populations()
ax = populations[populations.t >= 1].plot("t", "particles",
                                          style= "o-")
ax.set_xlabel("Generation");
plt.savefig('./out/basico_generations.png')