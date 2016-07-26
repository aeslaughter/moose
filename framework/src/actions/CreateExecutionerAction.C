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

#include "CreateExecutionerAction.h"
#include "Factory.h"
#include "PetscSupport.h"
#include "MooseApp.h"
#include "Executioner.h"

template<>
InputParameters validParams<CreateExecutionerAction>()
{
  InputParameters params = validParams<MooseObjectAction>();

  return params;
}


CreateExecutionerAction::CreateExecutionerAction(InputParameters params) :
    MooseObjectAction(params)
{
}

void
CreateExecutionerAction::act()
{
  // Deprecated support
  if (_moose_object_pars.get<bool>("trans_ss_check"))
  {
    InputParameters params = _factory.getValidParams("RelativeSolutionDifferenceNorm");
    params.set<std::vector<OutputName> >("outputs") = {"none"};
    _problem->addPostprocessor("_moose_l2_norm", "RelativeSolutionDifferenceNorm", params);
  }

  _moose_object_pars.set<FEProblem *>("_fe_problem") = _problem.get();
  MooseSharedPointer<Executioner> executioner = _factory.create<Executioner>(_type, "Executioner", _moose_object_pars);

  _app.executioner() = executioner;
}
