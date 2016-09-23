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

// MOOSE includes
#include "LevelSetMeshRefinementTransfer.h"
#include "LevelSetExecutioner.h"
#include "FEProblem.h"
#include "MultiApp.h"
#include "Adaptivity.h"

template<>
InputParameters validParams<LevelSetMeshRefinementTransfer>()
{
  InputParameters params = validParams<MultiAppCopyTransfer>();

  params.set<MooseEnum>("direction") = "TO_MULTIAPP";
  params.suppressParameter<MooseEnum>("direction");

  params.set<MultiMooseEnum>("execute_on") = "CUSTOM";
  params.suppressParameter<MultiMooseEnum>("execute_on");

  return params;
}

LevelSetMeshRefinementTransfer::LevelSetMeshRefinementTransfer(const InputParameters & parameters) :
    MultiAppCopyTransfer(parameters)
{
}

void
LevelSetMeshRefinementTransfer::initialSetup()
{
  if (std::dynamic_pointer_cast<MooseSharedPointer<LevelSetExecutioner>>(_app.executioner()))
    mooseError("The LevelSetMeshRefinementTransfer must be used with a LevelSetExecutioner.");

  FEProblem & from_problem = _multi_app->problem();
  for (unsigned int i = 0; i < _multi_app->numGlobalApps(); i++)
    if (_multi_app->hasLocalApp(i))
    {
      std::cout << "SETUP SUPAPP adaptivity----------------------------------------------" << std::endl;
      FEProblem & to_problem = _multi_app->appProblem(i);
      MooseVariable & to_var = to_problem.getVariable(0, _to_var_name);
      Adaptivity & adapt = to_problem.adaptivity();
      adapt.setMarkerVariableName(to_var.name());
      adapt.setCyclesPerStep(from_problem.adaptivity().getCyclesPerStep());
      adapt.init(0, 0);
      adapt.setUseNewSystem();
      adapt.setMaxHLevel(from_problem.adaptivity().getMaxHLevel());
      adapt.setAdpaptivityOn(false);
    }
}

void
LevelSetMeshRefinementTransfer::execute()
{
  MultiAppCopyTransfer::execute();

  for (unsigned int i = 0; i < _multi_app->numGlobalApps(); i++)
    if (_multi_app->hasLocalApp(i))
    {
      FEProblem & to_problem = _multi_app->appProblem(i);
      Adaptivity & adapt = to_problem.adaptivity();
      adapt.setAdpaptivityOn(true);
      to_problem.adaptMesh();
      adapt.setAdpaptivityOn(false);
    }
}
