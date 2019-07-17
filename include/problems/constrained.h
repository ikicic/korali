#ifndef _KORALI_PROBLEM_CONSTRAINED_H_
#define _KORALI_PROBLEM_CONSTRAINED_H_

#include "problems/base.h"

namespace Korali { namespace Problem {

class Constrained : public Base
{
 public:

 void packVariables(double* sample, Korali::Model& data) override;
 double evaluateFitness(Korali::Model& data) override;
 double evaluateLogPrior(double* sample) override;

 void initialize() override;
 void finalize() override;

 // Serialization Methods
 void getConfiguration() override;
 void setConfiguration() override;
};

} } // namespace Korali::Problem

#endif // _KORALI_PROBLEM_CONSTRAINED_H_