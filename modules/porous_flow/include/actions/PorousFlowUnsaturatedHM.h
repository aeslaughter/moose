/****************************************************************/
/* MOOSE - Multiphysics Object Oriented Simulation Environment  */
/*                                                              */
/*          All contents are licensed under LGPL V2.1           */
/*             See LICENSE for full restrictions                */
/****************************************************************/
#ifndef POROUSFLOWUSATURATEDHM_H
#define POROUSFLOWUSATURATEDHM_H

#include "PorousFlowUnsaturated.h"

class PorousFlowUnsaturatedHM;

template<>
InputParameters validParams<PorousFlowUnsaturatedHM>();

/**
 * A non-isothermal single phase, single component, partially or fully saturated fluid.
 * The fluid has constant bulk density, constant viscosity, constant specific heat capacity,
 * and its saturation is found using the van-Genuchten expression
 */
class PorousFlowUnsaturatedHM : public PorousFlowUnsaturated
{
public:
  PorousFlowUnsaturatedHM(const InputParameters & params);

  virtual void act() override;

protected:
  /// displacement NonlinearVariable names
  std::vector<NonlinearVariableName> _displacements;

  /// number of displacement variables supplied
  unsigned _ndisp;

  /// displacement Variable names
  std::vector<VariableName> _coupled_displacements;

  /// fluid specific heat capacity at constant volume
  Real _biot_coefficient;
};

#endif //POROUSFLOWUSATURATEDHM_H
