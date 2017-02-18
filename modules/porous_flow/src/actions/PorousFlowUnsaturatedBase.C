/****************************************************************/
/* MOOSE - Multiphysics Object Oriented Simulation Environment  */
/*                                                              */
/*          All contents are licensed under LGPL V2.1           */
/*             See LICENSE for full restrictions                */
/****************************************************************/
#include "PorousFlowUnsaturatedBase.h"

#include "Factory.h"
#include "FEProblem.h"
#include "Parser.h"
#include "libmesh/string_to_enum.h"

template<>
InputParameters validParams<PorousFlowUnsaturatedBase>()
{
  InputParameters params = validParams<Action>();
  params.addRequiredParam<NonlinearVariableName>("porepressure", "The name of the porepressure variable");
  params.addParam<RealVectorValue>("gravity", RealVectorValue(0.0, 0.0, -10.0), "Gravitational acceleration vector downwards (m/s^2)");
  MooseEnum simulation_type_choice("steady=0 transient=1", "transient");
  params.addParam<MooseEnum>("simulation_type", simulation_type_choice, "Whether a transient or steady-state simulation is being performed");
  params.addRangeCheckedParam<Real>("van_genuchten_alpha", 1.0E-6, "van_genuchten_alpha > 0.0", "Van Genuchten alpha parameter used to determine saturation from porepressure");
  params.addRangeCheckedParam<Real>("van_genuchten_m", 0.6, "van_genuchten_m > 0 & van_genuchten_m < 1", "Van Genuchten m parameter used to determine saturation from porepressure");
  params.addParam<Real>("fluid_density0", 1000.0, "Density of the fluid at zero porepressure");
  params.addParam<Real>("fluid_bulk_modulus", 2.0E9, "Bulk modulus of the fluid");
  params.addParam<Real>("fluid_viscosity", 1.0E-3, "Viscosity of the fluid");
  MooseEnum relperm_type_choice("FLAC=0 Corey=1", "FLAC");
  params.addParam<MooseEnum>("relative_permeability_type", relperm_type_choice, "Type of relative-permeability function.  FLAC relperm = (1+m)S^m - mS^(1+m).  Corey relperm = S^m.  m is the exponent.");
  params.addRangeCheckedParam<Real>("relative_permeability_exponent", 3.0, "relative_permeability_exponent>=0", "Relative permeability exponent");
  params.addClassDescription("Adds Kernels and fluid-property Materials necessary to simulate a single-phase saturated-unsaturated flow problem.  The fluid is assumed to have constant bulk density and viscosity, and the saturation is computed using van Genuchten's expression.  This also adds a PorousFlowDictator UserObject called 'dictator'.");
  return params;
}

PorousFlowUnsaturatedBase::PorousFlowUnsaturatedBase(const InputParameters & params) :
    Action(params),
    _pp_var(getParam<NonlinearVariableName>("porepressure")),
    _coupled_pp_var(1),
    _gravity(getParam<RealVectorValue>("gravity")),
    _simulation_type(getParam<MooseEnum>("simulation_type")),
    _van_genuchten_alpha(getParam<Real>("van_genuchten_alpha")),
    _van_genuchten_m(getParam<Real>("van_genuchten_m")),
    _fluid_density0(getParam<Real>("fluid_density0")),
    _fluid_bulk_modulus(getParam<Real>("fluid_bulk_modulus")),
    _fluid_viscosity(getParam<Real>("fluid_viscosity")),
    _relperm_type(getParam<MooseEnum>("relative_permeability_type")),
    _relative_permeability_exponent(getParam<Real>("relative_permeability_exponent"))
{
  _coupled_pp_var[0] = _pp_var;
}

void
PorousFlowUnsaturatedBase::act()
{
  // add the dictator
  if (_current_task == "add_user_object")
  {
    std::string uo_name = "dictator";
    std::string uo_type = "PorousFlowDictator";
    InputParameters params = _factory.getValidParams(uo_type);
    params.set<std::vector<VariableName>>("porous_flow_vars") = _coupled_pp_var;
    params.set<unsigned int>("number_fluid_phases") = 1;
    params.set<unsigned int>("number_fluid_components") = 1;
    _problem->addUserObject(uo_type, uo_name, params);
  }

  // add the kernels
  if (_current_task == "add_kernel")
  {
    std::string kernel_name = "PorousFlowUnsaturatedBase_AdvectiveFlux";
    std::string kernel_type = "PorousFlowAdvectiveFlux";
    InputParameters params = _factory.getValidParams(kernel_type);
    params.set<NonlinearVariableName>("variable") = _pp_var;
    params.set<unsigned int>("fluid_component") = 0;
    params.set<UserObjectName>("PorousFlowDictator") = "dictator";
    params.set<RealVectorValue>("gravity") = _gravity;
    _problem->addKernel(kernel_type, kernel_name, params);
  }
  if (_current_task == "add_kernel" && _simulation_type == 1)
  {
    std::string kernel_name = "PorousFlowUnsaturatedBase_MassTimeDerivative";
    std::string kernel_type = "PorousFlowMassTimeDerivative";
    InputParameters params = _factory.getValidParams(kernel_type);
    params.set<NonlinearVariableName>("variable") = _pp_var;
    params.set<unsigned int>("fluid_component") = 0;
    params.set<UserObjectName>("PorousFlowDictator") = "dictator";
    _problem->addKernel(kernel_type, kernel_name, params);
  }

  // add materials
  if (_current_task == "add_material")
  {
    std::string material_type = "PorousFlow1PhaseP_VG";
    InputParameters params = _factory.getValidParams(material_type);

    std::string material_name = "PorousFlowUnsaturatedBase_1PhaseP_VG_qp";
    params.set<UserObjectName>("PorousFlowDictator") = "dictator";
    params.set<std::vector<VariableName>>("porepressure") = _coupled_pp_var;
    params.set<Real>("al") = _van_genuchten_alpha;
    params.set<Real>("m") = _van_genuchten_m;
    _problem->addMaterial(material_type, material_name, params);

    material_name = "PorousFlowUnsaturatedBase_1PhaseP_VG";
    params.set<bool>("at_nodes") = true;
    _problem->addMaterial(material_type, material_name, params);
  }
  if (_current_task == "add_material")
  {
    std::string material_type = "PorousFlowMassFraction";
    InputParameters params = _factory.getValidParams(material_type);

    std::string material_name = "PorousFlowUnsaturatedBase_MassFraction";
    params.set<UserObjectName>("PorousFlowDictator") = "dictator";
    params.set<bool>("at_nodes") = true;
    _problem->addMaterial(material_type, material_name, params);
  }
  if (_current_task == "add_material")
  {
    std::string material_type = "PorousFlowDensityConstBulk";
    InputParameters params = _factory.getValidParams(material_type);

    std::string material_name = "PorousFlowUnsaturatedBase_DensityConstBulk_qp";
    params.set<UserObjectName>("PorousFlowDictator") = "dictator";
    params.set<Real>("density_P0") = _fluid_density0;
    params.set<Real>("bulk_modulus") = _fluid_bulk_modulus;
    params.set<unsigned int>("phase") = 0;
    _problem->addMaterial(material_type, material_name, params);

    material_name = "PorousFlowUnsaturatedBase_DensityConstBulk";
    params.set<bool>("at_nodes") = true;
    _problem->addMaterial(material_type, material_name, params);

    // now join all results for all the phases together (there is only 1 phase in this situation)
    material_type = "PorousFlowJoiner";
    params = _factory.getValidParams(material_type);
    material_name = "PorousFlowUnsaturatedBase_Density_qp_all";
    params.set<UserObjectName>("PorousFlowDictator") = "dictator";
    params.set<std::string>("material_property") = "PorousFlow_fluid_phase_density_qp";
    _problem->addMaterial(material_type, material_name, params);

    material_name = "PorousFlowUnsaturatedBase_Density_all";
    params.set<std::string>("material_property") = "PorousFlow_fluid_phase_density_nodal";
    params.set<bool>("at_nodes") = true;
    params.set<bool>("include_old") = true;
    _problem->addMaterial(material_type, material_name, params);
  }
  if (_current_task == "add_material")
  {
    std::string material_type = "PorousFlowViscosityConst";
    InputParameters params = _factory.getValidParams(material_type);

    std::string material_name = "PorousFlowUnsaturatedBase_Viscosity";
    params.set<UserObjectName>("PorousFlowDictator") = "dictator";
    params.set<Real>("viscosity") = _fluid_viscosity;
    params.set<unsigned int>("phase") = 0;
    params.set<bool>("at_nodes") = true;
    _problem->addMaterial(material_type, material_name, params);

    // now join all results for all the phases together (there is only 1 phase in this situation)
    material_type = "PorousFlowJoiner";
    params = _factory.getValidParams(material_type);

    material_name = "PorousFlowUnsaturatedBase_Viscosity_all";
    params.set<UserObjectName>("PorousFlowDictator") = "dictator";
    params.set<bool>("at_nodes") = true;
    params.set<std::string>("material_property") = "PorousFlow_viscosity_nodal";
    _problem->addMaterial(material_type, material_name, params);
  }
  if (_current_task == "add_material")
  {
    std::string material_type;
    if (_relperm_type == 0)
      material_type = "PorousFlowRelativePermeabilityFLAC";
    else
      material_type = "PorousFlowRelativePermeabilityCorey";
    InputParameters params = _factory.getValidParams(material_type);

    std::string material_name = "PorousFlowUnsaturatedBase_RelativePermeability";
    params.set<UserObjectName>("PorousFlowDictator") = "dictator";
    if (_relperm_type == 0)
      params.set<Real>("m") = _relative_permeability_exponent;
    else
      params.set<Real>("n") = _relative_permeability_exponent;
    params.set<unsigned int>("phase") = 0;
    params.set<bool>("at_nodes") = true;
    _problem->addMaterial(material_type, material_name, params);

    // now join all results for all the phases together (there is only 1 phase in this situation)
    material_type = "PorousFlowJoiner";
    params = _factory.getValidParams(material_type);

    material_name = "PorousFlowUnsaturatedBase_RelativePermeability_all";
    params.set<UserObjectName>("PorousFlowDictator") = "dictator";
    params.set<bool>("at_nodes") = true;
    params.set<std::string>("material_property") = "PorousFlow_relative_permeability_nodal";
    _problem->addMaterial(material_type, material_name, params);
  }
    
  // add aux for saturation
  if (_current_task == "add_aux_variable")
    _problem->addAuxVariable("saturation", FEType(Utility::string_to_enum<Order>("CONSTANT"), Utility::string_to_enum<FEFamily>("MONOMIAL")));
  if (_current_task == "add_aux_kernel")
  {
    std::string aux_kernel_type = "MaterialStdVectorAux";
    InputParameters params = _factory.getValidParams(aux_kernel_type);

    std::string aux_kernel_name = "PorousFlowUnsaturatedBase_SaturationAux";
    params.set<MaterialPropertyName>("property") = "PorousFlow_saturation_qp";
    params.set<unsigned>("index") = 0;
    params.set<AuxVariableName>("variable") = "saturation";
    params.set<MultiMooseEnum>("execute_on") = "timestep_end";
    _problem->addAuxKernel(aux_kernel_type, aux_kernel_name, params);
  }
}
