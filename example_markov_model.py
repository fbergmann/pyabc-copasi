import numpy as np

def h(x, pre, c):
    return (x**pre).prod(1) * c

def gillespie(x, c, pre, post, max_t):
    """
    Gillespie simulation

    Parameters
    ----------

    x: 1D array of size n_species
        The initial numbers.

    c: 1D array of size n_reactions
        The reaction rates.

    pre: array of size n_reactions x n_species
        What is to be consumed.

    post: array of size n_reactions x n_species
        What is to be produced

    max_t: int
        Timulate up to time max_t

    Returns
    -------
    t, X: 1d array, 2d array
        t: The time points.
        X: The history of the species.
           ``X.shape == (t.size, x.size)``

    """
    t = 0
    t_store = [t]
    x_store = [x.copy()]
    S = post - pre

    while t < max_t:
        h_vec = h(x, pre, c)
        h0 = h_vec.sum()
        if h0 == 0:
            break
        delta_t = np.random.exponential(1 / h0)
        # no reaction can occur any more
        if not np.isfinite(delta_t):
            t_store.append(max_t)
            x_store.append(x)
            break
        reaction = np.random.choice(c.size, p=h_vec/h0)
        t = t + delta_t
        x = x + S[reaction]

        t_store.append(t)
        x_store.append(x)

    return np.array(t_store), np.array(x_store)



MAX_T = 0.1

class Model1:
    __name__ = "Model 1"
    x0 = np.array([40, 3])   # Initial molecule numbers
    pre = np.array([[1, 1]], dtype=int)
    post = np.array([[0, 2]])


    def __call__(self, par):
        t, X = gillespie(self.x0,
                         np.array([float(par["rate"])]),
                         self.pre, self.post,
                         MAX_T)
        return {"t": t, "X" : X}


class Model2(Model1):
    __name__ = "Model 2"
    pre = np.array([[1, 0]], dtype=int)
    post = np.array([[0, 1]])



if __name__ == "__main__":
    import matplotlib.pyplot as plt

    true_rate = 2.3
    observations = [Model1()({"rate": true_rate}),
                    Model2()({"rate": 30})]
    fig, axes = plt.subplots(ncols=2)
    fig.set_size_inches((12, 4))
    for ax, title, obs in zip(axes, ["Observation", "Competition"],
                            observations):
        ax.step(obs["t"], obs["X"]);
        ax.legend(["Species X", "Species Y"]);
        ax.set_xlabel("Time");
        ax.set_ylabel("Concentration");
        ax.set_title(title);

    plt.savefig('./out/orig_out.png')