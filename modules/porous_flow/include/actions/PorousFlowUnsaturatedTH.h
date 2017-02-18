/****************************************************************/
/* MOOSE - Multiphysics Object Oriented Simulation Environment  */
/*                                                              */
/*          All contents are licensed under LGPL V2.1           */
/*             See LICENSE for full restrictions                */
/****************************************************************/
#ifndef POROUSFLOWUSATURATEDTH_H
#define POROUSFLOWUSATURATEDTH_H

#include "PorousFlowUnsaturatedBase.h"

class PorousFlowUnsaturatedTH;

template<>
InputParameters validParams<PorousFlowUnsaturatedTH>();

/**
 * A non-isothermal single phase, single component, partially or fully saturated fluid.
 * The fluid has constant bulk density, constant viscosity, constant specific heat capacity,
 * and its saturation is found using the van-Genuchten expression
 */
class PorousFlowUnsaturatedTH : public PorousFlowUnsaturatedBase
{
public:
  PorousFlowUnsaturatedTH(const InputParameters & params);

  virtual void act() override;

protected:
  /// temperature variable name
  VariableName _t_var;

  /// fluid specific heat capacity at constant volume
  Real _fluid_cv;
};

#endif //POROUSFLOWUSATURATEDTH_H
