#!/usr/bin/env python3
import os
import sys
sys.path.append('./model/')
from work import *

import numpy as np

# Ns: number of samples to draw per variable
Ns = 100

# fileName: output directory
fileName = 'samplesOut.dat'

# Prepare file
prepareOutputDir()

# Variables
means = [-5, 5]
variances = [1, 3]

# Creating new experiment
import korali
e = korali.Experiment()

e["Problem"]["Type"] = "Propagation"
e["Problem"]["Execution Model"] = lambda modelData: put_normal_rnds(modelData, Ns, fileName)
e["Variables"][0]["Name"] = "Mean"
e["Variables"][0]["Precomputed Values"] = means
e["Variables"][1]["Name"] = "Variance"
e["Variables"][1]["Precomputed Values"] = variances
e["Solver"]["Type"] = "Executor"
e["Solver"]["Executions Per Generation"] = 1
e["Console Output"]["Verbosity"] = "Detailed"

# Starting Korali's Engine and running experiment
k = korali.Engine()
k.run(e)

