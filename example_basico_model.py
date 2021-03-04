import numpy as np

from basico_forward import BasicoModel

if __name__ == "__main__":
    import matplotlib.pyplot as plt


    MAX_T = 0.1
    true_rate = 2.3
    observations = [BasicoModel('./data/abc_example_model1.xml', MAX_T)({"rate": true_rate}),
                    BasicoModel('./data/abc_example_model2.xml', MAX_T)({"rate": 30}), 
                     ]
    fig, axes = plt.subplots(ncols=2)
    fig.set_size_inches((12, 4))
    for ax, title, obs in zip(axes, ["Basico (Observation)","Basico (Competition)"],
                            observations):
        ax.step(obs["t"], obs["X"]);
        ax.legend(["Species X", "Species Y"]);
        ax.set_xlabel("Time");
        ax.set_ylabel("Concentration");
        ax.set_title(title);

    plt.savefig('./out/basico_out.png')