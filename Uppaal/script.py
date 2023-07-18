from os import system
import subprocess
import re
from model1 import model

# constants in order to verify the validity of the parameters chosen
distance0 = 8
distance4 = 10
maxDistance = 17
SOC0 = 60
SOCmax = 100

findTestsResults = r"Verifying formula (\d*)(?:.*?)Formula is(.*?)satisfied"

pathVerifyta = "../../Downloads/uppaal64-4.1.26-2/uppaal64-4.1.26-2/bin-Windows/verifyta.exe"
pathXMLModelToVerify = "modelToVerify.xml"

def checkValidityInScript(Cdis, V):
    # t0.Init imply (t0.SOC >= t0.Cdis*t0.estimatedTimeTravelling())
    #       int estimatedTimeTravelling(){return nextDistance() * 60 / V}
    # t0.SOCmax >= (maxDistance*t0.Cdis*60/t0.V)
    if (SOC0 >= Cdis * (distance4 * 60 / V)) and (SOCmax >= maxDistance * Cdis * 60 / V):
        return True

    return False


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


def checkEnoughSOC(asserts):
    return checkProperties(asserts, 0, 1)


def checkInTime(asserts):
    return checkProperties(asserts, 1, 2)


def generateModel(processingTime, numberOfPodUnit, speedConveyorBeltUnit, branchArray, switchArray, posArray):
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
                                        placeholder6 = procTime)
                            )
    print(f"\nCreated model for speedConveyorBelt={speedConveyorBeltUnit}, numberOfPod={numberOfPodUnit} and processingTime={procTime} ")


def restartFromLastChecked(lastChecked, minTimeInStation, strategy, Crec, Cdis, V):
    if (lastChecked[0] < minTimeInStation):
        return True
    elif (lastChecked[0] > minTimeInStation):
        return False
    else:
        if (lastChecked[1] < strategy):
            return True
        elif (lastChecked[1] > strategy):
            return False
        else:
            if (lastChecked[2] < Crec):
                return True
            elif (lastChecked[2] > Crec):
                return False
            else:
                if (lastChecked[3] < Cdis):
                    return True
                elif (lastChecked[3] > Cdis):
                    return False
                else:
                    if (lastChecked[4] < V):
                        return True
                    elif (lastChecked[4] >= V):
                        return False

numberOfPod = [2, 3, 4]
speedConveyorBelt = [2, 4, 7] 
processingTimes = [[5, 10, 15, 20, 25, 30],
                   [1, 2, 3, 4, 5, 6],
                   [2, 4, 6, 8, 10, 12]]
# in order to let you stop and continue the script from where you left,
# you can modify this with the last completed check values
lastChecked = [0, 0, 0, 0, 0]   # [1, 2, 3, 10, 150]
timeout = 7 * 60                # seconds: 7 minutes

with open("dataModels1.csv", "a") as csv:
    csv.write("NumberOfPods,stationProcessingTime,speedConveyorBelt\n")
    for speedConveyorBeltUnit in speedConveyorBelt:
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
                axisNumPod = []
                axisProcTime = []
                status = []
                generateModel(processingTime, numberOfPodUnit, speedConveyorBeltUnit, branchArray, switchArray, posArray)

                verified = 0
                asserts = [0, 0, 0, 0, 0, 0, 0, 0]
                # executing the verification of the model with UPPAAL
                try:
                    output = subprocess.run([pathVerifyta, pathXMLModelToVerify], stdout=subprocess.PIPE,
                                            stderr=subprocess.DEVNULL, timeout=timeout)
                    asserts = parseResults(output.stdout.decode('utf-8'))
                    print(asserts)
                    verified = (checkInTime(asserts) << 1) + checkEnoughSOC(asserts)
                except subprocess.TimeoutExpired:
                    verified = -1
                    print(f"\tSKIPPED: verification took more than {timeout} seconds: terminated")

                # parsing the result of the checks
                print("\tENOUGH SOC: " + str(checkEnoughSOC(asserts)) +
                        "\tMAX DELAY: " + str(checkInTime(asserts)) + " " +
                        "\tResult: " + str(verified))
                csv.write(f"{numberOfPodUnit},{speedConveyorBeltUnit},{config},{verified}\n")
                axisSpeed.append(speedConveyorBeltUnit)
                axisNumPod.append(numberOfPodUnit)
                axisProcTime.append(config)
                status.append(verified)


print("ANALYSIS COMPLETE!")

