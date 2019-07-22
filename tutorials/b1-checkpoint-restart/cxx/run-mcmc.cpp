// In this example, we demonstrate how a Korali experiment can
// be resumed from any point (generation). This is a useful feature
// for continuing jobs after an error, or to fragment big jobs into
// smaller ones that can better fit a supercomputer queue.

// First, we run a simple Korali experiment.

#include "korali.hpp"
#include "model/model.h"

int main(int argc, char* argv[])
{
 auto k = Korali::Engine();

 k["Problem"]["Type"] = "Sampling";

 k["Variables"][0]["Name"] = "X";
 k["Variables"][0]["Initial Mean"] = 0.0;
 k["Variables"][0]["Initial Standard Deviation"] = 1.0;

 k["Solver"]["Type"] = "MCMC";
 k["Solver"]["Burn In"] = 500;
 k["Solver"]["Max Chain Length"] = 5000;

 k["General"]["Console Output"]["Frequency"] = 1000;
 k["General"]["Results Output"]["Frequency"] = 1000;

 k.setModel(model);
 k.run();

 printf("\n\nRestarting now:\n\n");

 // Now we loadState() to resume the same experiment from generation 5.
 k.loadState("_korali_result/s01000.json");

 k.run();
}