import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.ticker as ticker
from mpl_toolkits.mplot3d import Axes3D

# Global parameters

file = f"config_1_final"


def color(status):
    if status == -1:  # timeout
        return ["Timeout", "grey"]
    elif status == 0:  # failed both
        return ["Failed all", "#FF0000"]
    elif status == 1:  # passed enoughSOC
        return ["Passed the first not the second", "yellow"]
    elif status == 2:  # passed trainsInTime
        return ["Passed the second not the first", "orange"]
    elif status == 3:  # passed both
        return ["Passed both", "green"]
    
def colorResult(resultMax,resultMin):
    if resultMax == -1:  # timeout
        return ["Timeout", "grey"]
    elif resultMax == 0 and resultMin==0:  # failed both
        return ["Failed all", "#FF0000"]
    elif resultMax == 1 and resultMin==0:  # passed enoughSOC
        return ["Passed MaxTime but not MinTime", "yellow"]
    elif resultMax == 0 and resultMin==1:  # passed trainsInTime
        return ["Passed MinTime but not MaxTime", "orange"]
    elif resultMax == 1 and resultMin==1:  # passed both
        return ["Passed both", "green"]


fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111, projection='3d')

ax.set_title(f"Configuration 1")
ax.set_xlabel("Number of Pods") 
ax.set_ylabel("ProcessingTime Configuration")
ax.set_zlabel("Speed of Conveyor Belt")

# generating legend
legend_elements = []
labels = []
for i in range(5):
    label, c = color(i - 1)
    legend_elements.append(Line2D([0], [0], color=c, marker='o', label=label))
    labels.append(label)

with open(file + ".csv", "r") as csv:
    line = csv.readline()

    for line in csv.readlines():
        [speed,NumberOfPods,config,resultMax,resultMin] = line.split(',')

        label, c = colorResult(int(resultMax),int(resultMin))
        ax.scatter(int(NumberOfPods), int(config),int(speed), c=c, s=100, linewidths=0.2)  # , s=size)  # plot the point (2,3,4) on the figure
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

