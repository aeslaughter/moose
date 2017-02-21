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
#include "TestAddMaterialAction.h"
#include "Factory.h"
#include "FEProblemBase.h"

template<>
InputParameters validParams<TestAddMaterialAction>()
{
  InputParameters params = validParams<Action>();
  params.addClassDescription("A test action for testing block restriction behavior when a material is added via an action.");
  return params;
}

TestAddMaterialAction::TestAddMaterialAction(const InputParameters & params) :
    Action(params)
{
}

void
TestAddMaterialAction::act()
{
  const std::string type = "GenericConstantMaterial";
  InputParameters params = _factory.getValidParams(type);
  _problem->addMaterial(type, "MOOSE_testing_add_material_from_action", params);
}
