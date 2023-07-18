import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.ticker as ticker
# Global parameters

file = f"dataModels1"


def color(status):
    if status == -1:  # timeout
        return ["Timeout", "grey"]
    elif status == 0:  # failed both
        return ["Failed all", "#FF0000"]
    elif status == 1:  # passed enoughSOC
        return ["Passed only one", "orange"]
    elif status == 2:  # passed trainsInTime
        return ["Passed only two", "orange"]
    elif status == 3:  # passed both
        return ["Passed only three", "orange"]
    elif status == 4:  # passed both
        return ["Passed only four", "#00FFFF"]
    elif status == 5:  # passed both
        return ["Passed all five query", "#00FF00"]
    else:
        print("Something's wrong with status {}".format(status))
        return ["Invalid", "#000000"]


fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111, projection='3d')

ax.set_title(f"Multi-Parameter Analysis")
ax.set_xlabel("Number of Pods") 
ax.set_ylabel("Configuration Number")
ax.set_zlabel("maxTime")

# generating legend
legend_elements = []
labels = []
for i in range(7):
    label, c = color(i - 1)
    legend_elements.append(Line2D([0], [0], color=c, marker='o', label=label))
    labels.append(label)

with open(file + ".csv", "r") as csv:
    line = csv.readline()

    for line in csv.readlines():
        [NumberOfPods,config,maxTime,result] = line.split(',')

        label, c = color(int(result))
        ax.scatter(int(NumberOfPods), int(config),int(maxTime), c=c, s=100, linewidths=0.2)  # , s=size)  # plot the point (2,3,4) on the figure
ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
ax.zaxis.set_major_locator(ticker.MaxNLocator(integer=True))
ax.view_init(elev=20, azim=-30)
ax.set_proj_type('ortho')
ax.invert_xaxis()
fig.tight_layout()
ax.legend(handles=legend_elements, labels=labels)
plt.savefig('my_plot.png')
plt.show()

