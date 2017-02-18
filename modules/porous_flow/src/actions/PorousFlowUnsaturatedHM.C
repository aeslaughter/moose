/****************************************************************/
/* MOOSE - Multiphysics Object Oriented Simulation Environment  */
/*                                                              */
/*          All contents are licensed under LGPL V2.1           */
/*             See LICENSE for full restrictions                */
/****************************************************************/
#include "PorousFlowUnsaturatedHM.h"

#include "Conversion.h"
#include "Factory.h"
#include "FEProblem.h"
#include "Parser.h"

template<>
InputParameters validParams<PorousFlowUnsaturatedHM>()
{
  InputParameters params = validParams<PorousFlowUnsaturated>();
  params.addRequiredParam<std::vector<NonlinearVariableName>>("displacements", "The name of the displacement variables");
  params.addParam<Real>("biot_coefficient", 1.0, "The Biot coefficient");
  params.addClassDescription("Adds Kernels and fluid-property Materials necessary to simulate an isothermal single-phase saturated-unsaturated flow problem, including mechanical deformation.  The fluid is assumed to have constant bulk density,, and constant viscosity, and the saturation is computed using van Genuchten's expression.  This also adds a PorousFlowDictator UserObject called 'dictator'.  To run a simulation you will also need to provide Material permeability, solid mechanical properties (young's modulus, etc), and porosity if for transient simulations, on each block.");
  return params;
}

PorousFlowUnsaturatedHM::PorousFlowUnsaturatedHM(const InputParameters & params) :
    PorousFlowUnsaturated(params),
    _displacements(getParam<std::vector<NonlinearVariableName>>("displacements")),
    _ndisp(_displacements.size()),
    _coupled_displacements(_ndisp),
    _biot_coefficient(getParam<Real>("biot_coefficient"))
{
  // convert vector of NonlinearVariableName to vector of VariableName
  for (unsigned int i = 0; i < _ndisp; ++i)
    _coupled_displacements[i] = _displacements[i];
}

void
PorousFlowUnsaturatedHM::act()
{
  // THE FOLLOWING DOES NOT WORK.
  // See pp_generation_action.i for an example: comment out the "vol_strain" material and PorousFlow_volumetric_strain_rate_qp is not defined; leave the "vol_strain" uncommented and PorousFlow_volumetric_strain_rate_qp is multiply defined (by a bunch of completely unrelated Materials!)
  if (_current_task == "add_material")
  {
    std::string material_type = "PorousFlowVolumetricStrain";
    InputParameters params = _factory.getValidParams(material_type);

    std::string material_name = "PorousFlowUnsaturatedHM_VolumetricStrain";
    params.set<UserObjectName>("PorousFlowDictator") = "dictator";
    params.set<std::vector<VariableName>>("displacements") = _coupled_displacements;
    _problem->addMaterial(material_type, material_name, params);
  }


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
    for (unsigned i = 0; i < _ndisp; ++i)
    {
      std::string kernel_name = "PorousFlowUnsaturatedHM_grad_stress" + Moose::stringify(i);
      std::string kernel_type = "StressDivergenceTensors";
      InputParameters params = _factory.getValidParams(kernel_type);
      params.set<NonlinearVariableName>("variable") = _displacements[i];
      params.set<std::vector<VariableName> >("displacements") = _coupled_displacements;
      params.set<unsigned>("component") = i;
      _problem->addKernel(kernel_type, kernel_name, params);

      if (_gravity(i) != 0)
      {
	kernel_name = "PorousFlowUnsaturatedHM_gravity" + Moose::stringify(i);
	kernel_type = "Gravity";
	params = _factory.getValidParams(kernel_type);
	params.set<NonlinearVariableName>("variable") = _displacements[i];
	params.set<Real>("value") = _gravity(i);
	_problem->addKernel(kernel_type, kernel_name, params);
      }

      kernel_name = "PorousFlowUnsaturatedHM_EffStressCoupling" + Moose::stringify(i);
      kernel_type = "PorousFlowEffectiveStressCoupling";
      params = _factory.getValidParams(kernel_type);
      params.set<UserObjectName>("PorousFlowDictator") = "dictator";
      params.set<NonlinearVariableName>("variable") = _displacements[i];
      params.set<Real>("biot_coefficient") = _biot_coefficient;
      params.set<unsigned>("component") = i;
      _problem->addKernel(kernel_type, kernel_name, params);
    }
  }
  if (_current_task == "add_kernel" && _simulation_type == 1)
  {
    std::string kernel_name = "PorousFlowUnsaturatedHM_MassVolumetricExpansion";
    std::string kernel_type = "PorousFlowMassVolumetricExpansion";
    InputParameters params = _factory.getValidParams(kernel_type);
    params.set<NonlinearVariableName>("variable") = _pp_var;
    params.set<UserObjectName>("PorousFlowDictator") = "dictator";
    params.set<unsigned>("fluid_component") = 0;
    _problem->addKernel(kernel_type, kernel_name, params);
  }
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
    std::string material_type = "PorousFlowTemperature";
    InputParameters params = _factory.getValidParams(material_type);

    std::string material_name = "PorousFlowUnsaturated_Temperature_qp";
    params.set<UserObjectName>("PorousFlowDictator") = "dictator";
    _problem->addMaterial(material_type, material_name, params);

    material_name = "PorousFlowUnsaturated_Temperature";
    params.set<bool>("at_nodes") = true;
    _problem->addMaterial(material_type, material_name, params);
  }
  if (_current_task == "add_material")
  {
    std::string material_type = "PorousFlow1PhaseP_VG";
    InputParameters params = _factory.getValidParams(material_type);

    std::string material_name = "PorousFlowUnsaturatedBase_1PhaseP_VG_qp";
    params.set<UserObjectName>("PorousFlowDictator") = "dictator";
    params.set<std::vector<VariableName>>("porepressure") = _coupled_pp_var;
    params.set<Real>("al") = _van_genuchten_alpha;
    params.set<Real>("m") = _van_genuchten_m;
    //_problem->addMaterial(material_type, material_name, params);

    material_name = "PorousFlowUnsaturatedBase_1PhaseP_VG";
    params.set<bool>("at_nodes") = true;
    //_problem->addMaterial(material_type, material_name, params);
  }
  if (_current_task == "add_material")
  {
    std::string material_type = "PorousFlowMassFraction";
    InputParameters params = _factory.getValidParams(material_type);

    std::string material_name = "PorousFlowUnsaturatedBase_MassFraction";
    params.set<UserObjectName>("PorousFlowDictator") = "dictator";
    params.set<bool>("at_nodes") = true;
    //_problem->addMaterial(material_type, material_name, params);
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
    //_problem->addMaterial(material_type, material_name, params);

    material_name = "PorousFlowUnsaturatedBase_Density_all";
    params.set<std::string>("material_property") = "PorousFlow_fluid_phase_density_nodal";
    params.set<bool>("at_nodes") = true;
    params.set<bool>("include_old") = true;
    //_problem->addMaterial(material_type, material_name, params);
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
    //_problem->addMaterial(material_type, material_name, params);
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
    //_problem->addMaterial(material_type, material_name, params);
  }
  if (_current_task == "add_material")
  {
    std::string material_type = "PorousFlowEffectiveFluidPressure";
    InputParameters params = _factory.getValidParams(material_type);

    std::string material_name = "PorousFlowUnsaturated_EffectiveFluidPressure_qp";
    params.set<UserObjectName>("PorousFlowDictator") = "dictator";
    _problem->addMaterial(material_type, material_name, params);

    material_name = "PorousFlowUnsaturated_EffectiveFluidPressure";
    params.set<bool>("at_nodes") = true;
    _problem->addMaterial(material_type, material_name, params);
  }
}
