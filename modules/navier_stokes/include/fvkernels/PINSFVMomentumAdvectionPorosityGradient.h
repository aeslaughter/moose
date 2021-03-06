//* This file is part of the MOOSE framework
//* https://www.mooseframework.org
//*
//* All rights reserved, see COPYRIGHT for full restrictions
//* https://github.com/idaholab/moose/blob/master/COPYRIGHT
//*
//* Licensed under LGPL 2.1, please see LICENSE for details
//* https://www.gnu.org/licenses/lgpl-2.1.html

#pragma once

#include "FVElementalKernel.h"

/**
 * A flux kernel diffusion of momentum in porous media across cell faces
 */
class PINSFVMomentumAdvectionPorosityGradient : public FVElementalKernel
{
public:
  static InputParameters validParams();
  PINSFVMomentumAdvectionPorosityGradient(const InputParameters & params);

protected:
  ADReal computeQpResidual() override;

  /// porosity variable to compute gradients
  const MooseVariableFV<Real> * const _eps_var;
  /// superficial velocity x-component
  const ADVariableValue & _u;
  /// superficial velocity y-component
  const ADVariableValue & _v;
  /// superficial velocity z-component
  const ADVariableValue & _w;
  /// density
  const Real & _rho;
  /// which momentum component this kernel applies to
  const int _index;
  /// whether the porosity has discontinuities that the Rhie Chow interpolation should avoid
  const bool _smooth_porosity;
};
