/****************************************************************/
/* MOOSE - Multiphysics Object Oriented Simulation Environment  */
/*                                                              */
/*          All contents are licensed under LGPL V2.1           */
/*             See LICENSE for full restrictions                */
/****************************************************************/
#ifndef POROUSFLOWUNSATURATED_H
#define POROUSFLOWUNSATURATED_H

#include "PorousFlowUnsaturatedBase.h"

class PorousFlowUnsaturated;

template<>
InputParameters validParams<PorousFlowUnsaturated>();

/**
 * An isothermal single phase, single component, partially or fully saturated fluid.
 * The fluid has constant bulk density, constant viscosity,
 * and its saturation is found using the van-Genuchten expression
 */
class PorousFlowUnsaturated : public PorousFlowUnsaturatedBase
{
public:
  PorousFlowUnsaturated(const InputParameters & params);

  virtual void act() override;
};

#endif //POROUSFLOWUNSATURATED_H
