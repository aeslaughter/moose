//* This file is part of the MOOSE framework
//* https://www.mooseframework.org
//*
//* All rights reserved, see COPYRIGHT for full restrictions
//* https://github.com/idaholab/moose/blob/master/COPYRIGHT
//*
//* Licensed under LGPL 2.1, please see LICENSE for details
//* https://www.gnu.org/licenses/lgpl-2.1.html

#include "MooseVariableBase.h"
#include "SubProblem.h"
#include "SystemBase.h"
#include "Assembly.h"
#include "MooseMesh.h"
#include "MooseApp.h" //TODO:MooseVariableToMooseObject
#include "InputParameterWarehouse.h" //TODO:MooseVariableToMooseObject

#include "libmesh/variable.h"
#include "libmesh/dof_map.h"
#include "libmesh/fe_type.h"
#include "libmesh/string_to_enum.h"

template<>
InputParameters
validParams<MooseVariableBase>()
{
  InputParameters params = validParams<MooseObject>();
  params += validParams<BlockRestrictable>();

  MooseEnum order("CONSTANT=0 FIRST=1 SECOND=2 THIRD=3 FOURTH=4", "FIRST", true);
  params.addParam<MooseEnum>("order", order, "Order of the FE shape function to use for this variable (additional orders not listed here are allowed, depending on the family).");

  MooseEnum family("LAGRANGE=0 MONOMIAL=2 HERMITE=22 SCALAR=31 HIERARCHIC=1 CLOUGH=21 XYZ=5 SZABAB=4 BERNSTEIN=3 L2_LAGRANGE=7 L2_HIERARCHIC=6", "LAGRANGE");
  params.addParam<MooseEnum>("family", family, "Specifies the family of FE shape functions to use for this variable.");

  params.addParam<Real>("initial_condition", "Specifies the initial condition for this variable");

  // Advanced input options
  params.addParam<Real>("scaling", 1.0, "Specifies a scaling factor to apply to this variable");
  params.addParam<bool>("eigen", false, "True to make this variable an eigen variable");
  params.addParamNamesToGroup("scaling eigen", "Advanced");

  params.registerBase("MooseVariableBase");
  params.addPrivateParam<SystemBase *>("_system_base");
  params.addPrivateParam<FEProblemBase *>("_fe_problem_base");
  params.addPrivateParam<Moose::VarKindType>("_var_kind");
  params.addPrivateParam<unsigned int>("_var_num");
  return params;
}

MooseVariableBase::MooseVariableBase(const InputParameters & parameters) :
    MooseObject(parameters),
    BlockRestrictable(this),
    _sys(*getParam<SystemBase *>("_system_base")), //TODO: get from _fe_problem_base
    _fe_type(Utility::string_to_enum<Order>(getParam<MooseEnum>("order")),
             Utility::string_to_enum<FEFamily>(getParam<MooseEnum>("family"))),
    _var_num(getParam<unsigned int>("_var_num")),
    _var_kind(getParam<Moose::VarKindType>("_var_kind")),
    _subproblem(_sys.subproblem()),
    _variable(_sys.system().variable(_var_num)),
    _assembly(_subproblem.assembly(getParam<THREAD_ID>("_tid"))),
    _dof_map(_sys.dofMap()),
    _mesh(_subproblem.mesh()),
    _scaling_factor(getParam<Real>("scaling"))
{

  std::cout << "Variable " << _name << " " << _var_num << " " << number() << std::endl;

}

const std::vector<dof_id_type> &
MooseVariableBase::allDofIndices() const
{
  const auto it = _sys.subproblem()._var_dof_map.find(name());
  if (it != _sys.subproblem()._var_dof_map.end())
    return it->second;
  else
    mooseError("VariableAllDoFMap not prepared for ",
               name(),
               " . Check nonlocal coupling requirement for the variable.");
}

Order
MooseVariableBase::order() const
{
  return _fe_type.order;
}
