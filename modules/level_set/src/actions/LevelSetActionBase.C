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
#include "LevelSetActionBase.h"
#include "LevelSetVelocityInterface.h"

// MOOSE includes
#include "FEProblem.h"

template<>
InputParameters validParams<LevelSetActionBase>()
{
  InputParameters params = validParams<Action>();
  params += validParams<LevelSetVelocityInterface<> >();
  params.addRequiredParam<NonlinearVariableName>("variable", "The levelset variable name.");
  return params;
}


LevelSetActionBase::LevelSetActionBase(InputParameters parameters) :
    Action(parameters),
    _variable_name(getParam<NonlinearVariableName>("variable"))
{
}


void
LevelSetActionBase::injectVariableParam(InputParameters & params)
{
  params.set<NonlinearVariableName>("variable") = _variable_name;
}


void
LevelSetActionBase::injectVelocityParams(InputParameters & params)
{
  auto helper = [this, &params](const std::string & name)
  {
    params.set<std::vector<VariableName> >(name) = _pars.get<std::vector<VariableName> >(name);
    if (_pars.hasDefaultCoupledValue(name))
      params.defaultCoupledValue(name, _pars.defaultCoupledValue(name));
  };

  helper("velocity_x");
  helper("velocity_y");
  helper("velocity_z");
}
