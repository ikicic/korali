#include "korali.h"

using json = nlohmann::json;

Korali::Parameter::Gaussian::Gaussian() : Korali::Parameter::Base::Base()
{
	_mean = 0.0;
	_sigma = 1.0;
};

double Korali::Parameter::Gaussian::getDensity(double x)
{
 return gsl_ran_gaussian_pdf(x - _mean, _sigma);
}

double Korali::Parameter::Gaussian::getDensityLog(double x)
{
 // Optimize by pre-calculating constants and using multiplication instead of power.
 return -0.5*log(2*M_PI) - log(_sigma) - 0.5*pow((x-_mean)/_sigma, 2);
}

double Korali::Parameter::Gaussian::getRandomNumber()
{
 return _mean + gsl_ran_gaussian(_range, _sigma);
}

double Korali::Parameter::Gaussian::logLikelihood(double sigma, int nData, double* x, double* u)
{
 if (nData == 0)
 {
  fprintf(stderr, "[Korali] Error: _problem's reference dataset not defined for the Likelihood (use: _problem.setReferenceData()).\n");
   return 0.0;
 }

 double sigma2 = sigma*sigma;
 double ssn = 0.0;

 for(int i = 0; i < nData; i++)
  {
  double diff = x[i] - u[i];
  ssn += diff*diff;
  }

 double res = 0.5* (nData*log(2*M_PI) + nData*log(sigma2) + ssn/sigma2);

 // printf("Sigma: %.11f - Res: %f\n", sigma, res);

 return res;
}

json Korali::Parameter::Gaussian::getConfiguration()
{
 auto js = this->Korali::Parameter::Base::getConfiguration();
 return js;
}

void Korali::Parameter::Gaussian::setConfiguration(json js)
{
	this->Korali::Parameter::Base::setConfiguration(js);

  if (js.find("Distribution") != js.end())
  {
    json dist = js["Distribution"];
    if (dist.find("Mean") != dist.end()) if (dist["Mean"].is_number())
    { _mean = dist["Mean"]; dist.erase("Mean"); }
    if (dist.find("Sigma") != dist.end()) if (dist["Sigma"].is_number())
    { _sigma = dist["Sigma"]; dist.erase("Sigma"); }
  }
}

