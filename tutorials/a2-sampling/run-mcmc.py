#!/usr/bin/env python3

# In this example, we demonstrate how Korali samples the posterior
# distribution in a bayesian problem where the likelihood
# is provided directly by the computational model.
# In this case, we use the MCMC method.

# Importing computational model
import sys
sys.path.append('./model')
from model import *

# Starting Korali's Engine
import korali
k = korali.initialize()

# Selecting problem and solver types.
k["Problem"]["Type"] = "Sampling"

# Defining problem's variables and their MCMC settings
k["Variables"][0]["Name"] = "X"
k["Variables"][0]["Initial Mean"] = 0.0
k["Variables"][0]["Initial Standard Deviation"] = 1.0

# Configuring the MCMC sampler parameters
k["Solver"]["Type"]  = "MCMC" 
k["Solver"]["Burn In"] = 500
k["Solver"]["Termination Criteria"]["Max Chain Length"] = 5000

# Setting Model
k.setDirectModel(model)

# Running Korali
k.run()