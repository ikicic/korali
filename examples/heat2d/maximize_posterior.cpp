#include "model/heat2d.hpp"
#include "korali.h"

int main(int argc, char* argv[])
{
 auto korali = Korali::Engine();

 korali["Seed"] = 0xC0FFEE;
 korali["Verbosity"] = "Detailed";

 korali["Problem"]["Type"] = "Bayesian";
 korali["Problem"]["Variables"][0]["Name"] = "Intensity";
 korali["Problem"]["Variables"][0]["Type"] = "Computational";
 korali["Problem"]["Variables"][0]["Distribution"] = "Uniform";
 korali["Problem"]["Variables"][0]["Minimum"] = 10.0;
 korali["Problem"]["Variables"][0]["Maximum"] = 60.0;

 korali["Problem"]["Variables"][1]["Name"] = "PosX";
 korali["Problem"]["Variables"][1]["Type"] = "Computational";
 korali["Problem"]["Variables"][1]["Distribution"] = "Uniform";
 korali["Problem"]["Variables"][1]["Minimum"] = 0.0;
 korali["Problem"]["Variables"][1]["Maximum"] = 0.5;

 korali["Problem"]["Variables"][2]["Name"] = "PosY";
 korali["Problem"]["Variables"][2]["Type"] = "Computational";
 korali["Problem"]["Variables"][2]["Distribution"] = "Uniform";
 korali["Problem"]["Variables"][2]["Minimum"] = 0.6;
 korali["Problem"]["Variables"][2]["Maximum"] = 1.0;

 korali["Problem"]["Variables"][3]["Name"] = "Sigma";
 korali["Problem"]["Variables"][3]["Type"] = "Statistical";
 korali["Problem"]["Variables"][3]["Distribution"] = "Uniform";
 korali["Problem"]["Variables"][3]["Minimum"] = 0.0;
 korali["Problem"]["Variables"][3]["Maximum"] = 20.0;

 auto p = heat2DInit();
 for (size_t i = 0; i < p.refTemp.size(); i++)
	 korali["Problem"]["Reference Data"][i] = p.refTemp[i];

 korali["Solver"]["Method"] = "CMA-ES";
 korali["Solver"]["Lambda"] = 32;

 korali.run([](Korali::ModelData& d) { heat2DSolver(d.getParameters(), d.getResults()); });

 return 0;
}