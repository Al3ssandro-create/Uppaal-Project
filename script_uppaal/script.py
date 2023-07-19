from os import system
import subprocess
import re
from model2 import model

# constants in order to verify the validity of the parameters chosen

findTestsResults = r"Verifying formula (\d*)(?:.*?)Formula is(.*?)satisfied"

pathVerifyta = "/home/vittorio/Scrivania/IDE/uppaal64-4.1.25-5/bin-Linux/verifyta"
pathXMLModelToVerify = "modelToVerify.xml"



def parseResults(res):
    asserts = []
    regResults = re.findall(findTestsResults, res, re.DOTALL)
    for a in regResults:
        if (a[1] == ' NOT '):
            asserts.append(0)
        elif (a[1] == ' '):
            asserts.append(1)
        else:
            print(a)
            asserts.append(2)

    return asserts


def checkProperties(asserts, i, f):
    for a in asserts[i:f]:
        if (a != 1):
            return False

    return True


def checkNotSamePosition(asserts):
    return checkProperties(asserts, 0, 0)

def checkQueue(asserts):
    return checkProperties(asserts, 1, 1)

def checkDeadlock(asserts):
    return checkProperties(asserts, 2, 2)

def checkMaximumTime(asserts):
    return checkProperties(asserts, 3, 3)

def checkMaxOnePodPerStation(asserts):
    return checkProperties(asserts, 4, 4)

def generateModel(processingTime, numberOfPodUnit, maxTime, speedConveyorBeltUnit, branchArray, switchArray, posArray,minTime):
    with open(pathXMLModelToVerify, "w") as modelToCheck:
        procTime = "{" + ", ".join(str(num) for num in processingTime) + "}"
        branch = "{" + ", ".join(str(num) for num in branchArray) + "}"
        switch = "{" + ", ".join(str(num) for num in switchArray) + "}"
        pos = "{" + ", ".join(str(num) for num in posArray) + "}"
        modelToCheck.write(model.format(placeholder1 = numberOfPodUnit, 
                                        placeholder2 = speedConveyorBeltUnit,
                                        placeholder3 = branch,
                                        placeholder4 = switch,
                                        placeholder5 = pos,
                                        placeholder6 = procTime,
                                        placeholder7 = maxTime,
                                        placeholder8 = minTime)
                            )
    print(f"\nCreated model for speedConveyorBelt={speedConveyorBeltUnit}, numberOfPod={numberOfPodUnit} and processingTime={procTime} ")



numberOfPod = [2, 3]
speedConveyorBelt = [2] 
processingTimes = [[5, 10, 15, 20, 25, 30],
                   [20, 30, 30, 20, 40, 20],
                   [10, 10, 30, 30, 10, 10]]
maxTimes = [150,250,550]
# in order to let you stop and continue the script from where you left,
# you can modify this with the last completed check values
lastChecked = [0, 0, 0, 0, 0]   # [1, 2, 3, 10, 150]
timeout = 15 * 60                # seconds: 7 minutes

with open("dataModels2.csv", "a") as csv:
    csv.write("Speed,minTImeconfig,pods,result\n")
    h=0
    minTime = [180]
    
    for i in range(len(speedConveyorBelt)):
        i=i-1
        config = 0
        for processingTime in processingTimes:
            config = config + 1
            print(config)
            for numberOfPodUnit in numberOfPod:
                branchArray = []
                switchArray = []
                posArray = []
                for i in range(numberOfPodUnit):
                    branchArray.append(0)
                    switchArray.append(-1)
                    posArray.append(i)
                # for time constraints we check the validity in the script
                axisSpeed = []
                axisMaxTime = []
                axisProcTime = []
                status = []
                generateModel(processingTime=processingTime, numberOfPodUnit= numberOfPodUnit,  speedConveyorBeltUnit= speedConveyorBelt[i], branchArray= branchArray, switchArray= switchArray, posArray= posArray,minTime=minTime[i],maxTime=0)

                verified = 0
                asserts = [0, 0, 0, 0, 0, 0, 0, 0]
                # executing the verification of the model with UPPAAL
                try:
                    output = subprocess.run([pathVerifyta, pathXMLModelToVerify], stdout=subprocess.PIPE,
                                            stderr=subprocess.DEVNULL, timeout=timeout)
                    asserts = parseResults(output.stdout.decode('utf-8'))
                    print(asserts)
                    verified = checkNotSamePosition(asserts) + checkQueue(asserts) + checkDeadlock(asserts) + checkMaximumTime(asserts) +checkMaxOnePodPerStation(asserts)
                except subprocess.TimeoutExpired:
                    verified = -1
                    print(f"\tSKIPPED: verification took more than {timeout} seconds: terminated")

                # parsing the result of the checks
                print("NOT SAME POSITION: " + str(checkNotSamePosition(asserts)) +
                        "\tQUEUE CORRECT LENGTH: " + str(checkQueue(asserts))  +
                        "\tNO DEADLOCK: " + str(checkDeadlock(asserts)) +
                        "\tNOT GO OVER MAXIMUM TIME: " + str(checkMaximumTime(asserts)) +
                        "\tONE POD PER STATION: " + str(checkMaxOnePodPerStation(asserts)) + " " +
                        "\tResult: " + str(verified))
                csv.write(f"{speedConveyorBelt[0]},{minTime[0]},{config},{numberOfPodUnit},{verified},{asserts}\n")
                ##  axisSpeed.append(speedConveyorBeltUnit)
                axisMaxTime.append(minTime[i])
                axisProcTime.append(config)
                status.append(verified)
print("ANALYSIS COMPLETE!")

