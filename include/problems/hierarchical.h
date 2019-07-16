#ifndef _KORALI_PROBLEM_HIERARCHICAL_H_
#define _KORALI_PROBLEM_HIERARCHICAL_H_

#include "problems/base.h"

namespace Korali { namespace Problem {

enum operationType  {SamplePsi, SampleTheta};

class Hierarchical : public Base
{
 public:

 // Reference Data
 operationType  _operationType;

 void packVariables(double* sample, Korali::Model& data) override;
 double evaluateFitness(Korali::Model& data) override;
 double evaluateLogPrior(double* sample) override;

 void initialize() override;
 void finalize() override;

 static void samplePsi(Korali::Model& data);
 static void sampleTheta(Korali::Model& data);

 // Serialization Methods
 void getConfiguration() override;
 void setConfiguration() override;

};

} } // namespace Korali::Problem


#endif // _KORALI_PROBLEM_HIERARCHICAL_H_