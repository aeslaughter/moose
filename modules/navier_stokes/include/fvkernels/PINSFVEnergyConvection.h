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

class INSFVEnergyVariable;

/**
 * An elemental kernel for transfering energy between the solid and fluid phases by convection
 */
class PINSFVEnergyConvection : public FVElementalKernel
{
public:
  static InputParameters validParams();

  PINSFVEnergyConvection(const InputParameters & parameters);

protected:
  ADReal computeQpResidual() override;

  /// the convective heat transfer coefficient
  const ADMaterialProperty<Real> & _h_solid_fluid;
  /// fluid temperature
  const ADVariableValue & _temp_fluid;
  /// solid temperature
  const ADVariableValue & _temp_solid;
  /// whether this kernel is being used for a solid or a fluid temperature
  const bool _is_solid;
};
