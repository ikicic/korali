#include "korali.h"

using json = nlohmann::json;

json Korali::Parameter::Base::getConfiguration()
{
 auto js = json();
 return js;
}

void Korali::Parameter::Base::setConfiguration(json js)
{
  _name = "Unnamed Parameter";
  _lowerBound = -1.0;
  _upperBound = 1.0;
  _minStdDevChange = 0.0;
  _type = KORALI_COMPUTATIONAL;

  if (js.find("Name") != js.end()) if (js["Name"].is_string())
  { _name = js["Name"]; js.erase("Name"); }

  bool typeDefined = false;
  if (js.find("Type") != js.end()) if (js["Type"].is_string())
  {
   if (js["Type"] == "Computational") { _type = KORALI_COMPUTATIONAL; typeDefined = true; };
   if (js["Type"] == "Statistical")   { _type = KORALI_STATISTICAL;   typeDefined = true; };
  }

  if (typeDefined) js.erase("Type");
  else fprintf(stderr,"[Korali] Warning: Type not defined for parameter \'%s\'. Assuming Computational.\n", _name.c_str());

  if (js.find("Bounds") != js.end())
  {
    json bounds = js["Bounds"];
    if (bounds.find("Lower") != bounds.end()) if (bounds["Lower"].is_number())
    { _lowerBound = bounds["Lower"]; bounds.erase("Lower"); }
    if (bounds.find("Upper") != bounds.end()) if (bounds["Upper"].is_number())
    { _upperBound = bounds["Upper"]; bounds.erase("Upper"); }
  }

  if (_upperBound <= _lowerBound)
  {
   fprintf(stderr, "[Korali] Warning: Invalid lower/upper bounds for %s.\n", _name.c_str());
   fprintf(stderr, "[Korali] Tip: Use parameter.setBounds(lower,upper); to define bounds.\n");
  }

  _initialValue = (_lowerBound + _upperBound) * 0.5;
  _initialStdDev = (_upperBound - _lowerBound) * 0.25;

  if (js.find("Initial Mean") != js.end()) if (js["Initial Mean"].is_number())
  { _initialValue = js["Initial Mean"]; js.erase("Initial Mean"); }

  if(_initialValue < _lowerBound || _initialValue > _upperBound)
   fprintf(stderr,"[Korali] Warning: Initial Value (%.4f) for \'%s\' is out of bounds (%.4f-%.4f).\n", _initialValue, _name.c_str(), _lowerBound, _upperBound);

  if (js.find("Initial StdDev") != js.end()) if (js["Initial StdDev"].is_number())
  { _initialStdDev = js["Initial StdDev"]; js.erase("Initial StdDev"); }

  if (js.find("Min StdDev Change") != js.end()) if (js["Min StdDev Change"].is_number())
  { _minStdDevChange = js["Min StdDev Change"]; js.erase("Min StdDev Change"); }
}
