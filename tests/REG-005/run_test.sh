#!/bin/bash

source ../functions.sh

cmaes_criteria=(
"Max Generations" 
"Max Generations" 
"Max Model Evaluations" 
"Max Infeasible Resamplings" 
"Min Value Difference Threshold"
"Min Standard Deviation" 
"Max Standard Deviation"
"Max Condition Covariance Matrix" 
"Max Value" 
"Min Value"
)

cmaes_values=(
0     # Max Generations
2     # Max Generations
20    # Max Model Evaluations
1     # Max Infeasible Resamplings
0.1   # Min Value Difference Threshold
0.1   # Min Standard Deviation
0.9   # Max Standard Deviation
1.0   # Max Condition Covariance
-1.2  # Max Value
-1.0  # Min Value
)

dea_criteria=(
"Max Generations" 
"Max Generations" 
"Max Model Evaluations" 
"Max Infeasible Resamplings" 
"Max Value" 
"Min Value Difference Threshold"
"Min Step Size" 
"Min Value"
)

dea_values=(
0     # Max Generations
2     # Max Generations
20    # Max Model Evaluations
0     # Max Infeasible Resamplings
-1.2  # Max Value
0.1   # Min Value Difference Threshold
0.3   # Min Step Size
-1.0  # Min Value
)

tmcmc_criteria=(
"Max Generations" 
"Max Generations" 
"Max Model Evaluations" 
"Target Annealing Exponent"
)

tmcmc_values=(
0     # Max Generations
1     # Max Generations
600   # Max Model Evaluations
0.6   # Target Annealing Exponent
)

#################################################
# CMA-ES Termination Criterion Tests
#################################################

logEcho "[Korali] Beginning CMA-ES termination criterion tests"

for ((i=0;i<${#cmaes_criteria[@]};++i)); do

  logEcho "-------------------------------------"
  logEcho "Testing Termination Criterion: ${cmaes_criteria[$i]}"
  logEcho "Running File: cmaes_termination.py"

  python3 ./cmaes_termination.py --criterion "${cmaes_criteria[$i]}" --value ${cmaes_values[$i]} >> $logFile 2>&1
  check_result

  log "[Korali] Removing results..."
  rm -rf "_korali_result" >> $logFile 2>&1
  check_result

  logEcho "-------------------------------------"

done


#################################################
# DEA Termination Criterion Tests
#################################################

logEcho "[Korali] Beginning DEA termination criterion tests"

for ((i=0;i<${#dea_criteria[@]};++i)); do

  logEcho "-------------------------------------"
  logEcho "Testing Termination Criterion: ${dea_criteria[$i]}"
  logEcho "Running File: dea_termination.py"

  python3 ./dea_termination.py --criterion "${dea_criteria[$i]}" --value ${dea_values[$i]} >> $logFile 2>&1
  check_result

  log "[Korali] Removing results..."
  rm -rf "_korali_result" >> $logFile 2>&1
  check_result

  logEcho "-------------------------------------"

done


#################################################
# TMCMC Termination Criterion Tests
#################################################

logEcho "[Korali] Beginning TMCMC termination criterion tests"

for ((i=0;i<${#tmcmc_criteria[@]};++i)); do

  logEcho "-------------------------------------"
  logEcho "Testing Termination Criterion: ${tmcmc_criteria[$i]}"
  logEcho "Running File: tmcmc_termination.py"

  python3 ./tmcmc_termination.py --criterion "${tmcmc_criteria[$i]}" --value ${tmcmc_values[$i]} >> $logFile 2>&1
  check_result

  log "[Korali] Removing results..."
  rm -rf "_korali_result" >> $logFile 2>&1
  check_result

  logEcho "-------------------------------------"

done