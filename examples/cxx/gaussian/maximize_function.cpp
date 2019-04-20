#include "korali.h"
#include "model/gaussian.h"

int main(int argc, char* argv[])
{
 size_t nPars = 4;

 gaussian_init(nPars);

 auto korali = Korali::Engine(gaussian);

 korali["Seed"] = 0xC0FFEE;
 korali["Verbosity"] = "Normal";

 for (size_t i = 0; i < nPars; i++)
 {
  korali["Parameters"][i]["Name"] = "X" + std::to_string(i);
  korali["Parameters"][i]["Type"] = "Computational";
  korali["Parameters"][i]["Distribution"] = "Uniform";
  korali["Parameters"][i]["Minimum"] = -32.0;
  korali["Parameters"][i]["Maximum"] = +32.0;
 }

 korali["Problem"]["Objective"] = "Direct Evaluation";
 korali["Solver"]["Method"] = "CMA-ES";
 korali["Solver"]["Termination Criteria"]["Min DeltaX"] = 1e-11;
 korali["Solver"]["Lambda"] = 128;

 korali.run();

 return 0;
}
