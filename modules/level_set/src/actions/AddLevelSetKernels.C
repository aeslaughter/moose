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
#include "AddLevelSetKernels.h"
#include "LevelSetVelocityInterface.h"

// MOOSE includes
#include "FEProblem.h"

template<>
InputParameters validParams<AddLevelSetKernels>()
{
  InputParameters params = validParams<LevelSetActionBase>();
  return params;
}

AddLevelSetKernels::AddLevelSetKernels(InputParameters parameters) :
    LevelSetActionBase(parameters)
{
}

void
AddLevelSetKernels::act()
{
  // TimeDerivative
  // \frac{\partial\phi}{\partial t}
  {
    InputParameters params = _factory.getValidParams("TimeDerivative");
    injectVariableParam(params);
    _problem->addKernel("TimeDerivative", "LevelSet:TimeDerivative", params);
  }

  // LevelSetAdvection
  // \vec{v} \cdot \nabal\phi
  {
    InputParameters params = _factory.getValidParams("LevelSetAdvection");
    injectVariableParam(params);
    injectVelocityParams(params);
    _problem->addKernel("LevelSetAdvection", "LevelSet:Advection", params);
  }
}
