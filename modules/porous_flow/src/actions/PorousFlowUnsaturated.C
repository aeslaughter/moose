/****************************************************************/
/* MOOSE - Multiphysics Object Oriented Simulation Environment  */
/*                                                              */
/*          All contents are licensed under LGPL V2.1           */
/*             See LICENSE for full restrictions                */
/****************************************************************/
#include "PorousFlowUnsaturated.h"

#include "Factory.h"
#include "FEProblem.h"
#include "Parser.h"

template<>
InputParameters validParams<PorousFlowUnsaturated>()
{
  InputParameters params = validParams<PorousFlowUnsaturatedBase>();
  params.addClassDescription("Adds Kernels and fluid-property Materials necessary to simulate a single-phase saturated-unsaturated flow problem.  The fluid is assumed to have constant bulk density and viscosity, and the saturation is computed using van Genuchten's expression.  This also adds a PorousFlowDictator UserObject called 'dictator'.  To run a simulation you will also need to provide Material permeability, and porosity if for transient simulations, on each block.  You may use the PorousFlowUnsaturatedMaterialAction classes to do this.");
  return params;
}

PorousFlowUnsaturated::PorousFlowUnsaturated(const InputParameters & params) :
    PorousFlowUnsaturatedBase(params)
{
}

void
PorousFlowUnsaturated::act()
{
  PorousFlowUnsaturatedBase::act();

  // add materials
  if (_current_task == "add_material")
  {
    std::string material_type = "PorousFlowTemperature";
    InputParameters params = _factory.getValidParams(material_type);

    std::string material_name = "PorousFlowUnsaturated_Temperature_qp";
    params.set<UserObjectName>("PorousFlowDictator") = "dictator";
    _problem->addMaterial(material_type, material_name, params);

    material_name = "PorousFlowUnsaturated_Temperature";
    params.set<bool>("at_nodes") = true;
    _problem->addMaterial(material_type, material_name, params);
  }
}
