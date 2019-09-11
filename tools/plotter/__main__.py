#! /usr/bin/env python3
import os
import sys
import signal
import json
import argparse
import matplotlib
import importlib

curdir = os.path.abspath(os.path.dirname(os.path.realpath(__file__))) 

def main(path, allFiles, live, generation, mean, check, test):

 if (check == True):
  print("[Korali] Plotter correctly installed.")
  exit(0)
 
 if (test == True):
     matplotlib.use('Agg')

 if ( (live == True) and (generation is not None)):
    print("korali.plotter: error: argument --live and argument --generation "\
            "GENERATION cannot be combined")
  
 if ( (live == True) and (allFiles is not None)):
    print("korali.plotter: error: argument --live and argument --all "\
            "cannot be combined")
 
    exit(-1)

 from korali.plotter.helpers import sig
 signal.signal(signal.SIGINT, sig)
 
 firstResult = path + '/initial.json'
 if ( not os.path.isfile(firstResult) ):
  print("[Korali] Error: Did not find any results in the {0} folder...".format(path))
  exit(-1)

 with open(firstResult) as f:
  data  = json.load(f)
 
 requestedSolver = data['Solver']['Type']
 
 # Detecting solvers
 solversDir = curdir + '/../solvers/'
 for moduleDir, relDir, fileNames in os.walk(solversDir):
  for fileName in fileNames: 
   if '.json' in fileName:
    with open(moduleDir + '/' + fileName, 'r') as file: moduleConfig = json.load(file)
    solverAlias = moduleConfig.get('Alias', '') 
    if (solverAlias == requestedSolver):
     solverName = fileName.replace('.json', '')
     solverFileName = moduleDir + '/' + solverName + '.py'
     print('Appending: ' + moduleDir)
     sys.path.append(moduleDir)
     solverLib = importlib.import_module(solverName, package=None)
     solverLib.plot(path, allFiles, live, generation, test, mean)
     exit(0)

 print("[Korali] Error: Did not recognize method for plotting...")
 exit(-1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='korali.plotter', description='Process korali results in _korali_result (default) folder.')
    parser.add_argument('--dir', help='directory of result files', default='_korali_result', required = False)
    parser.add_argument('--all', help='plot all available results', action='store_true', required = False)
    parser.add_argument('--live', help='no auto close, keep polling for new result files', action='store_true', required = False)
    parser.add_argument('--generation', help='plot results of generation GENERATION', action='store', type=int, required = False)
    parser.add_argument('--mean', help='plot mean of objective variables', action='store_true', required = False)
    parser.add_argument('--check', help='verifies that korali.plotter is available', action='store_true', required = False)
    parser.add_argument('--test', help='run without graphics (for testing purpose)', action='store_true', required = False)
    args = parser.parse_args()

    main( args.dir, args.all, args.live, args.generation, args.mean, args.check, args.test)