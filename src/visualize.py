"""Matplotlib drawing of the road network and the final delivery route."""
import matplotlib
matplotlib.use("Agg")          # draw to files, no window needed
import matplotlib.pyplot as plt


def plot_route(nodes, graph, full_path, tour, title, out_file):
    fig, ax = plt.subplots(figsize=(9, 7))
    # all roads in light grey
    for u, nbrs in graph.items():
        for v, _ in nbrs:
            if u < v:
                ax.plot([nodes[u][1], nodes[v][1]], [nodes[u][2], nodes[v][2]],
                        color="#cccccc", linewidth=1, zorder=1)
    # driven roads in red with arrows
    for a, b in zip(full_path, full_path[1:]):
        ax.annotate("", xy=(nodes[b][1], nodes[b][2]), xytext=(nodes[a][1], nodes[a][2]),
                    arrowprops=dict(arrowstyle="->", color="#d62728", lw=1.8), zorder=3)
    stops = set(tour)
    others = [n for n in nodes if n not in stops]
    ax.scatter([nodes[n][1] for n in others], [nodes[n][2] for n in others],
               s=40, color="#9aa5b1", zorder=2, label="road junction")
    ax.scatter([nodes[n][1] for n in stops if n != tour[0]],
               [nodes[n][2] for n in stops if n != tour[0]],
               s=110, color="#1f77b4", zorder=4, label="delivery stop")
    ax.scatter([nodes[tour[0]][1]], [nodes[tour[0]][2]], s=220, marker="s",
               color="#2ca02c", zorder=5, label="warehouse")
    for order, n in enumerate(tour[:-1]):      # number the stops in visiting order
        ax.text(nodes[n][1] + 0.25, nodes[n][2] + 0.25,
                "W" if order == 0 else str(order), fontsize=10, fontweight="bold", zorder=6)
    ax.set_title(title)
    ax.set_xlabel("x (km)")
    ax.set_ylabel("y (km)")
    ax.legend(loc="best")
    ax.set_aspect("equal", adjustable="datalim")
    fig.tight_layout()
    fig.savefig(out_file, dpi=150)
    plt.close(fig)
