#!/usr/bin/env python3

# In this example, we demonstrate how Korali finds values for the
# variables that maximize the objective function, given by a
# user-provided computational model, subject to a set of
# constraints.
#
# Importing the computational model and constraints
import sys
sys.path.append('./model')
from g09 import *

# Starting Korali's Engine
import korali
k = korali.initialize()

# Setting model and constraints
k.setModel( g09 )
k.addConstraint( g1 )
k.addConstraint( g2 )
k.addConstraint( g3 )
k.addConstraint( g4 )

# Selecting problem type
k["Problem"] = "Direct Evaluation"

# Selecting the CCMA-ES solver
k["Solver"]  = "CMAES"
k["Seed"]    = 5772
k["CMAES"]["Objective"] = "Maximize"

# Creating 7 variables and
# Setting up the variables CCMA-ES bounds
nParams = 7
for i in range(nParams) :
  k["Variables"][i]["Name"] = "X" + str(i)
  k["Variables"][i]["CMAES"]["Lower Bound"] = -10.0
  k["Variables"][i]["CMAES"]["Upper Bound"] = +10.0

# Configuring the constrained optimizer CCMA-ES
k["CMAES"]["Is Sigma Bounded"] = True
k["CMAES"]["Sample Count"] = 32
k["CMAES"]["Viability Sample Count"] = 4
k["CMAES"]["Termination Criteria"]["Max Fitness"]["Enabled"] = True
k["CMAES"]["Termination Criteria"]["Max Fitness"]["Value"] = -680.630057374402 - 1e-4

# Reducing Output
k["Termination Criteria"]["Max Generations"] = 500
k["Verbosity"] = "Minimal"

# Setting output directory
k["Result Directory"] = "_b2_constrained_optimization_result"

# Running Korali
k.run()
