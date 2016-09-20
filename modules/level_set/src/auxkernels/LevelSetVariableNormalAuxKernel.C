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

#include "LevelSetVariableNormalAuxKernel.h"

template<>
InputParameters validParams<LevelSetVariableNormalAuxKernel>()
{
  InputParameters params = validParams<AuxKernel>();
  params.addRequiredCoupledVar("levelset_variable", "The variable to compare the thresold value against");
  MooseEnum component("x=0 y=1 z=2");
  params.addRequiredParam<MooseEnum>("component", component, "The normal component to compute.");
  return params;
}

LevelSetVariableNormalAuxKernel::LevelSetVariableNormalAuxKernel(const InputParameters & parameters) :
    AuxKernel(parameters),
    _grad_levelset_variable(coupledGradient("levelset_variable")),
    _component(getParam<MooseEnum>("component"))
{
}

Real
LevelSetVariableNormalAuxKernel::computeValue()
{
  RealVectorValue n = _grad_levelset_variable[_qp] / (_grad_levelset_variable[_qp].size() + std::numeric_limits<Real>::epsilon());
  return n(_component);
}
