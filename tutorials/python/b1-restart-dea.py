#!/usr/bin/env python3

## In this example, we demonstrate how a Korali experiment can
## be resumed from any point (generation). This is a useful feature
## for continuing jobs after an error, or to fragment big jobs into
## smaller ones that can better fit a supercomputer queue.

## First, we run a simple Korali experiment.

import sys
sys.path.append('./model')
from directModel import *

import korali
k = korali.initialize()
k.setModel(evaluateModel)

k["Problem"] = "Direct Evaluation"
k["Solver"]  = "DEA"

k["Variables"][0]["Name"] = "X"
k["Variables"][0]["DEA"]["Lower Bound"] = -10.0
k["Variables"][0]["DEA"]["Upper Bound"] = +10.0

k["DEA"]["Objective"] = "Maximize"
k["DEA"]["Sample Count"] = 10

# Setting output directory
k["Result Directory"] = "_b1_restart_dea"

# Reducing Output
k["Termination Criteria"]["Max Generations"] = 500
k["Console Output Frequency"] = 10

k.run()

print("\n\nRestart Now\n\n")

# Now we loadState() to resume the same experiment from generation 5
k.loadState("_b1_restart_dea/s00004.json")

k.run()