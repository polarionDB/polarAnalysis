from matplotlib import pyplot as plt 
import matplotlib as mpl
import json

def main():

    graph_data_white = json.loads(open("results/white_legal_moves.json").read())
    graph_data_black = json.loads(open("results/black_legal_moves.json").read())

    mpl.style.use("fast")

    fig, (whitesub, blacksub) = plt.subplots(2, 1)

    fig.suptitle("Average Legal Moves per Ply")
    whitesub.set_ylabel("Legal Moves Available (White)", fontsize=8)
    blacksub.set_xlabel("Ply Number")
    blacksub.set_ylabel("Legal Moves Available (Black)", fontsize=8)

    p1 = whitesub.scatter(graph_data_white['x'], graph_data_white['y'], label='White',alpha=1)
    p2 = blacksub.scatter(graph_data_black['x'], graph_data_black['y'], label='Black',alpha=1, color='orange')

    plt.savefig("results/average_legal_moves.png")
    plt.savefig("results/average_legal_moves.eps")

if __name__ == "__main__":
    main()