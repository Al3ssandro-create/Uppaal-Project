from os import system
import subprocess
import re
from model2 import model

# constants in order to verify the validity of the parameters chosen
FLAG = 1 ## Here we can change which parameter to analyze

findTestsResults = r"Verifying formula (\d+)(?:.*?)Formula is(.*?)satisfied.*?Pr\(([^)]+)\) in \[([\d.]+),([\d.]+)\].*?with confidence ([\d.]+)"

#Verifying formula 1 at /nta/queries/query[1]/formula
# -- Formula is satisfied.
#(29 runs) Pr([] ...) in [0.901855,1]
#with confidence 0.95.


pathVerifyta = "/home/simo/Downloads/uppaal64-4.1.26-2/bin-Linux/verifyta"
pathXMLModelToVerify = "modelToVerify2.xml"



def parseResults(res):
    asserts = []
    #print(res)
    regResults = re.findall(findTestsResults, res, re.DOTALL)
    #print(regResults)
    for a in regResults:
        if (a[1] == ' NOT ' or a[4] != '1'):
            asserts.append(0)
        elif (a[1] == ' ' and a[4]=='1'):
            asserts.append(1)
        else:
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

def generateModel(numberOfPodUnit, speedConveyorBeltUnit, branchArray, switchArray, posArray, errorsFirstSensorsUnit, errorsSecondSensorsUnit, meanAndVarianceUnit):
    with open(pathXMLModelToVerify, "w") as modelToCheck:
        branch = "{" + ", ".join(str(num) for num in branchArray) + "}"
        switch = "{" + ", ".join(str(num) for num in switchArray) + "}"
        pos = "{" + ", ".join(str(num) for num in posArray) + "}"
        errorsFirstSensorsArray = "{" + ", ".join(str(num) for num in errorsFirstSensorsUnit) + "}"
        errorsSecondSensorsArray = "{" + ", ".join(str(num) for num in errorsSecondSensorsUnit) + "}"
        meanAndVarianceMatrix = "{" + ", ".join("{" + ", ".join(str(num) for num in row) + "}" for row in meanAndVarianceUnit) + "}"
        modelToCheck.write(model.format(placeholder1 = numberOfPodUnit, 
                                        placeholder2 = speedConveyorBeltUnit,
                                        placeholder3 = branch,
                                        placeholder4 = switch,
                                        placeholder5 = pos,
                                        placeholder6 = errorsFirstSensorsArray,
                                        placeholder7 = errorsSecondSensorsArray,
                                        placeholder8 = meanAndVarianceMatrix)
                            )
    print(f"\nCreated model for speedConveyorBelt={speedConveyorBeltUnit}, numberOfPod={numberOfPodUnit}, errorsFirstSensors={errorsFirstSensorsUnit}, errorsSecondSensors={errorsSecondSensorsUnit}, meanAndVariance={meanAndVarianceUnit}")



numberOfPod = [4, 8, 12]
speedConveyorBelt = [2, 4, 7] 
meanAndVariance = [[[400,1],[400,1],[700,2],[800,4], [1270,1],[240,4]], 
                   [[40,1],[40,1],[70,2],[80,4], [127,1],[24,4]], 
                   [[4000,1],[4000,1],[7000,2],[8000,4], [12700,1],[2400,4]]]
errorsFirstSensors = [[50,50,50,50,50,50], [20,20,20,20,20,20], [1,1,1,1,1,1]]
errorsSecondSensors = [[50,50,50,50,50,50], [20,20,20,20,20,20], [1,1,1,1,1,1]]
maxTimes = [50,100,200]

# in order to let you stop and continue the script from where you left,
# you can modify this with the last completed check values
lastChecked = [0, 0, 0, 0, 0]   # [1, 2, 3, 10, 150]
timeout = 7 * 60                # seconds: 7 minutes
if(FLAG == 1):
    with open("dataModels1.csv", "a") as csv:
        csv.write("NumberOfPods,config,result\n")
        for errorsFirstSensorsSingle in errorsFirstSensors:
            for errorsSecondSensorsSingle in errorsSecondSensors: 
                for speedConveyorBeltUnit in speedConveyorBelt:
                    config = 0
                    for meanAndVarianceSingle in meanAndVariance:
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
                            axisNumPod = []
                            axisProcTime = []
                            status = []
                            generateModel(numberOfPodUnit, speedConveyorBeltUnit, branchArray, switchArray, posArray, errorsFirstSensorsSingle, errorsSecondSensorsSingle, meanAndVarianceSingle)
                            verified = 0
                            asserts = [0, 0, 0, 0, 0, 0, 0, 0]
                            # executing the verification of the model with UPPAAL
                            try:
                                output = subprocess.run([pathVerifyta, pathXMLModelToVerify], stdout=subprocess.PIPE,
                                                        stderr=subprocess.DEVNULL, timeout=timeout)
                                asserts = parseResults(output.stdout.decode('utf-8'))
                                print(asserts)
                                verified = checkNotSamePosition(asserts) + checkQueue(asserts) + checkDeadlock(asserts)
                            except subprocess.TimeoutExpired:
                                verified = -1
                                print(f"\tSKIPPED: verification took more than {timeout} seconds: terminated")

                            # parsing the result of the checks
                            print("NOT SAME POSITION: " + str(checkNotSamePosition(asserts)) +
                                    "\tQUEUE CORRECT LENGTH: " + str(checkQueue(asserts))  +
                                    "\tNO DEADLOCK: " + str(checkDeadlock(asserts)) +
                                    "\tResult: " + str(verified))
                            csv.write(f"{numberOfPodUnit},{config},{verified}\n")
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
                        generateModel(numberOfPodUnit, speedConveyorBeltUnit, branchArray, switchArray, posArray, errorsFirstSensorsSingle, errorsSecondSensorsSingle, meanAndVarianceSingle)

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

