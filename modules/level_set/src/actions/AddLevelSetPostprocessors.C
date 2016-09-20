/****************************************************************/
/*               DO NOT MODIFY THIS HEADER                      */
/* MOOSE - Multiphysics Object Oriented Simulation Environment  */
/*                                                              */
/*           (c) 2010 Battelle Energy Alliance, LLC             */
/*                   ALL RIGHTS RESERVED                        */
/*                                                              */
/*          Prepared by Battelle Energy Alliance, LLC           */
/*            Under Contract No. DE-AC07-05ID14517              */
/*            With the U. S. Department of Energy               */
/*                                                              */
/*            See COPYRIGHT for full restrictions               */
/****************************************************************/

// LevelSet includes
#include "AddLevelSetPostprocessors.h"
#include "LevelSetVelocityInterface.h"

// MOOSE includes
#include "FEProblem.h"

template<>
InputParameters validParams<AddLevelSetPostprocessors>()
{
  InputParameters params = validParams<LevelSetActionBase>();
  params.addParam<std::string>("cfl", "The name of the CFLCondition postprocessor to create.");
  params.addParam<Real>("cfl_coefficient", "The multiplier for the CFL condition.");

  MultiMooseEnum loc("inside outside", "inside");
  params.addParam<std::vector<std::string> >("volume", "The name(s) of the volume/area postprocessor(s) to create. The number of names must be equal to the number of 'volume_locations' and 'volume_levels' set.");
  params.addParam<MultiMooseEnum>("volume_location", loc, "The portion of the domain that should be considered for the volume/area calculation, if both 'inside' and 'outside' are provided the supplied name will be suffixed." );
  params.addParam<std::vector<Real> >("volume_threshold", "The threshold value of the level set variable to used for computing the area/volume." );

  return params;
}

AddLevelSetPostprocessors::AddLevelSetPostprocessors(InputParameters parameters) :
    LevelSetActionBase(parameters)
{
}

void
AddLevelSetPostprocessors::act()
{
  // CFL Condition
  if (isParamValid("cfl"))
  {
    InputParameters params = _factory.getValidParams("CFLCondition");
    injectVelocityParams(params);
    injectVariableParam(params);
    params.set<MultiMooseEnum>("execute_on") = "initial timestep_end";
    if (isParamValid("cfl_coefficient"))
      params.set<Real>("coefficient") = getParam<Real>("cfl_coefficient");
    _problem->addPostprocessor("CFLCondition", getParam<std::string>("cfl"), params);
  }

  // Volume/Area calculator
  if (isParamValid("volume"))
  {
    // Extract the names
    const std::vector<std::string> & name = getParam<std::vector<std::string> >("volume");
    const MultiMooseEnum & location = getParam<MultiMooseEnum>("volume_location");
    std::vector<Real> threshold = getParam<std::vector<Real> >("volume_threshold");

    // Populate the threshold, if empty
    if (threshold.empty())
      threshold.resize(name.size(), 0.0);

    // Check that all three items are the same length
    if (name.size() != location.size() || name.size() != threshold.size() || location.size() != threshold.size())
      mooseError("If a postprocessor name for the 'volume/area' is suppled then the following parameters must be all the same length:\n'volume'\n'volume_location'\n'volume_threshold (may also be empty)'");

    for (unsigned int i = 0; i < name.size(); ++i)
    {
      InputParameters params = _factory.getValidParams("LevelSetVolume");
      injectVelocityParams(params);
      params.set<std::vector<VariableName> >("variable") = std::vector<VariableName>(1, static_cast<VariableName>(_variable_name));
      params.set<MultiMooseEnum>("execute_on") = "initial timestep_end";
      params.set<MooseEnum>("location") = location[i];
      params.set<Real>("threshold") = threshold[i];
      _problem->addPostprocessor("LevelSetVolume", name[i], params);
    }
  }
}
