from os import system
import subprocess
import re
from model1 import model

# constants in order to verify the validity of the parameters chosen
FLAG = 1 ## Here we can change which parameter to analyze

findTestsResults = r"Verifying formula (\d*)(?:.*?)Formula is(.*?)satisfied"

pathVerifyta = "../../Downloads/uppaal64-4.1.26-2/uppaal64-4.1.26-2/bin-Windows/verifyta.exe"
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
    return checkProperties(asserts, 0, 1)

def checkQueue(asserts):
    return checkProperties(asserts, 1, 2)

def checkDeadlock(asserts):
    return checkProperties(asserts, 2, 3)

def checkMaximumTime(asserts):
    return checkProperties(asserts, 2, 3)

def checkMaxOnePodPerStation(asserts):
    return checkProperties(asserts, 2, 3)

def generateModel(processingTime, numberOfPodUnit, maxTime, speedConveyorBeltUnit, branchArray, switchArray, posArray):
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
                                        placeholder7 = maxTime)
                            )
    print(f"\nCreated model for speedConveyorBelt={speedConveyorBeltUnit}, numberOfPod={numberOfPodUnit} and processingTime={procTime} ")



numberOfPod = [2, 3, 4]
speedConveyorBelt = [2, 4, 7] 
processingTimes = [[5, 10, 15, 20, 25, 30],
                   [1, 2, 3, 4, 5, 6],
                   [2, 4, 6, 8, 10, 12]]
maxTimes = [50,100,200]
# in order to let you stop and continue the script from where you left,
# you can modify this with the last completed check values
lastChecked = [0, 0, 0, 0, 0]   # [1, 2, 3, 10, 150]
timeout = 20 * 60                # seconds: 7 minutes
if(FLAG == 1):
    with open("dataModels1.csv", "a") as csv:
        csv.write("NumberOfPods,config,maxTime,result\n")
        for maxTime in maxTimes:
            for speedConveyorBeltUnit in speedConveyorBelt:
                config = 0
                for processingTime in processingTimes:
                    config = config + 1
                    for numberOfPodUnit in numberOfPod:
                        branchArray = []
                        switchArray = []
                        posArray = []
                        for i in range(numberOfPodUnit):
                            branchArray.append(0)
                            switchArray.append(-1)
                            posArray.append(i)
                        # for time constraints we check the validity in the script
                        axisMaxTime = []
                        axisNumPod = []
                        axisProcTime = []
                        status = []
                        generateModel(processingTime, numberOfPodUnit, maxTime, 2, branchArray, switchArray, posArray)

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
                        csv.write(f"{numberOfPodUnit},{config},{maxTime},{verified}\n")
                        axisMaxTime.append(maxTime)
                        axisNumPod.append(numberOfPodUnit)
                        axisProcTime.append(config)
                        status.append(verified)
else:
    numberOfPod = [4]
    with open("dataModels2.csv", "a") as csv:
        csv.write("Speed,config,maxTime,result\n")
        for maxTime in maxTimes:
            for speedConveyorBeltUnit in speedConveyorBelt:
                config = 0
                for processingTime in processingTimes:
                    config = config + 1
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
                        generateModel(processingTime, numberOfPodUnit, maxTime, speedConveyorBeltUnit, branchArray, switchArray, posArray)

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
                        csv.write(f"{speedConveyorBeltUnit},{config},{maxTime},{verified}\n")
                        axisSpeed.append(speedConveyorBeltUnit)
                        axisMaxTime.append(maxTime)
                        axisProcTime.append(config)
                        status.append(verified)
print("ANALYSIS COMPLETE!")

