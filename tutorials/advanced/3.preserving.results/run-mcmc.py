#!/usr/bin/env python3

## In this example, we demonstrate how to use Korali to sample
## a computational model, while saving important quantities of
## interest derived from the model

# Importing computational model
import sys
sys.path.append('model')
from model import *

# Starting Korali's Engine
import korali
k = korali.Engine()
e = korali.Experiment()

# Selecting problem and solver types.
e["Problem"]["Type"] = "Sampling"
e["Problem"]["Objective Function"] = storeResults

# Defining the problem's variables and their CMA-ES bounds.
e["Variables"][0]["Name"] = "Soil pH"
e["Variables"][0]["Initial Mean"] = 6.0
e["Variables"][0]["Initial Standard Deviation"] = 1.0

e["Variables"][1]["Name"] = "Average Temperature (C)"
e["Variables"][1]["Initial Mean"] = +30.0
e["Variables"][1]["Initial Standard Deviation"] = +5.0

# Configuring the TMCMC sampler parameters
e["Solver"]["Type"] = "MCMC"
e["Solver"]["Burn In"] = 500
e["Solver"]["Termination Criteria"]["Max Samples"] = 2000

# Configuring output frequency
e["Console Output"]["Frequency"] = 500
e["File Output"]["Frequency"] = 500

# Storing sample information
e["File Output"]["Store Samples"] = True

# Running Korali
k.run(e)

e["Solver"]["Termination Criteria"]["Max Samples"] = 5000

# Running Korali
k.run(e)
