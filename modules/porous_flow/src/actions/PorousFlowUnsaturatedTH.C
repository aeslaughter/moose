/****************************************************************/
/* MOOSE - Multiphysics Object Oriented Simulation Environment  */
/*                                                              */
/*          All contents are licensed under LGPL V2.1           */
/*             See LICENSE for full restrictions                */
/****************************************************************/
#include "PorousFlowUnsaturatedTH.h"

#include "Factory.h"
#include "FEProblem.h"
#include "Parser.h"

template<>
InputParameters validParams<PorousFlowUnsaturatedTH>()
{
  InputParameters params = validParams<PorousFlowUnsaturatedBase>();
  params.addRequiredParam<NonlinearVariableName>("temperature", "The name of the temperature variable");
  params.addParam<Real>("fluid_specific_heat_capacity", 4180.0, "Specific heat capacity at constant volume of fluid (J/kg/K)");
  params.addClassDescription("Adds Kernels and fluid-property Materials necessary to simulate a non-isothermal single-phase saturated-unsaturated flow problem, including heat flow.  The fluid is assumed to have constant bulk density, constant specific heat capacity, and constant viscosity, and the saturation is computed using van Genuchten's expression.  This also adds a PorousFlowDictator UserObject called 'dictator'.  To run a simulation you will also need to provide Material permeability, conductivity, and porosity if for transient simulations, on each block.  You may use the PorousFlowUnsaturatedMaterialAction classes to do this.");
  return params;
}

PorousFlowUnsaturatedTH::PorousFlowUnsaturatedTH(const InputParameters & params) :
    PorousFlowUnsaturatedBase(params),
    _t_var(getParam<NonlinearVariableName>("temperature")),
    _fluid_cv(getParam<Real>("fluid_specific_heat_capacity"))
{
}

void
PorousFlowUnsaturatedTH::act()
{
  PorousFlowUnsaturatedBase::act();

  // add the kernels
  if (_current_task == "add_kernel")
  {
    std::string kernel_name = "PorousFlowUnsaturatedTH_HeatAdvection";
    std::string kernel_type = "PorousFlowHeatAdvection";
    InputParameters params = _factory.getValidParams(kernel_type);
    params.set<NonlinearVariableName>("variable") = _t_var;
    params.set<UserObjectName>("PorousFlowDictator") = "dictator";
    params.set<RealVectorValue>("gravity") = _gravity;
    _problem->addKernel(kernel_type, kernel_name, params);
  }
  if (_current_task == "add_kernel")
  {
    std::string kernel_name = "PorousFlowUnsaturatedTH_HeatConduction";
    std::string kernel_type = "PorousFlowHeatConduction";
    InputParameters params = _factory.getValidParams(kernel_type);
    params.set<NonlinearVariableName>("variable") = _t_var;
    params.set<UserObjectName>("PorousFlowDictator") = "dictator";
    _problem->addKernel(kernel_type, kernel_name, params);
  }
  if (_current_task == "add_kernel" && _simulation_type == 1)
  {
    std::string kernel_name = "PorousFlowUnsaturatedTH_EnergyTimeDerivative";
    std::string kernel_type = "PorousFlowEnergyTimeDerivative";
    InputParameters params = _factory.getValidParams(kernel_type);
    params.set<NonlinearVariableName>("variable") = _t_var;
    params.set<UserObjectName>("PorousFlowDictator") = "dictator";
    _problem->addKernel(kernel_type, kernel_name, params);
  }

  // add materials
  if (_current_task == "add_material")
  {
    std::string material_type = "PorousFlowTemperature";
    InputParameters params = _factory.getValidParams(material_type);

    std::string material_name = "PorousFlowUnsaturated_Temperature_qp";
    params.set<UserObjectName>("PorousFlowDictator") = "dictator";
    params.set<std::vector<VariableName>>("temperature") = {_t_var};
    _problem->addMaterial(material_type, material_name, params);

    material_name = "PorousFlowUnsaturated_Temperature";
    params.set<bool>("at_nodes") = true;
    _problem->addMaterial(material_type, material_name, params);
  }
  if (_current_task == "add_material")
  {
    std::string material_type = "PorousFlowInternalEnergyIdeal";
    InputParameters params = _factory.getValidParams(material_type);

    std::string material_name = "PorousFlowUnsaturatedTH_InternalEnergy";
    params.set<UserObjectName>("PorousFlowDictator") = "dictator";
    params.set<Real>("specific_heat_capacity") = _fluid_cv;
    params.set<unsigned int>("phase") = 0;
    params.set<bool>("at_nodes") = true;
    _problem->addMaterial(material_type, material_name, params);

    // now join all results for all the phases together (there is only 1 phase in this situation)
    material_type = "PorousFlowJoiner";
    params = _factory.getValidParams(material_type);

    material_name = "PorousFlowUnsaturatedTH_InternalEnergy_all";
    params.set<UserObjectName>("PorousFlowDictator") = "dictator";
    params.set<bool>("at_nodes") = true;
    params.set<std::string>("material_property") = "PorousFlow_fluid_phase_internal_energy_nodal";
    _problem->addMaterial(material_type, material_name, params);
  }
  if (_current_task == "add_material")
  {
    std::string material_type = "PorousFlowEnthalpy";
    InputParameters params = _factory.getValidParams(material_type);

    std::string material_name = "PorousFlowUnsaturatedTH_Enthalpy";
    params.set<UserObjectName>("PorousFlowDictator") = "dictator";
    params.set<unsigned int>("phase") = 0;
    params.set<bool>("at_nodes") = true;
    _problem->addMaterial(material_type, material_name, params);

    // now join all results for all the phases together (there is only 1 phase in this situation)
    material_type = "PorousFlowJoiner";
    params = _factory.getValidParams(material_type);

    material_name = "PorousFlowUnsaturatedTH_Enthalpy_all";
    params.set<UserObjectName>("PorousFlowDictator") = "dictator";
    params.set<bool>("at_nodes") = true;
    params.set<std::string>("material_property") = "PorousFlow_fluid_phase_enthalpy_nodal";
    _problem->addMaterial(material_type, material_name, params);
  }
}
