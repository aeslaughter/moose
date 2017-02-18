/****************************************************************/
/* MOOSE - Multiphysics Object Oriented Simulation Environment  */
/*                                                              */
/*          All contents are licensed under LGPL V2.1           */
/*             See LICENSE for full restrictions                */
/****************************************************************/
#ifndef POROUSFLOWUNSATURATEDBASE_H
#define POROUSFLOWUNSATURATEDBASE_H

#include "Action.h"

class PorousFlowUnsaturatedBase;

template<>
InputParameters validParams<PorousFlowUnsaturatedBase>();

/**
 * Base class for actions involving a
 * single phase, single component, partially or fully saturated fluid.
 * The fluid has constant bulk density, constant viscosity,
 * and its saturation is found using the van-Genuchten expression
 */
class PorousFlowUnsaturatedBase : public Action
{
public:
  PorousFlowUnsaturatedBase(const InputParameters & params);

  virtual void act() override;

protected:
  /// porepressure NonlinearVariable name
  NonlinearVariableName _pp_var;

  /// porepressure Variable name
  std::vector<VariableName> _coupled_pp_var;

  /// gravity
  RealVectorValue _gravity;

  /// whether steady or transient simulation
  MooseEnum _simulation_type;

  /// Van Genuchten alpha parameter
  Real _van_genuchten_alpha;

  /// Van Genuchten m parameter
  Real _van_genuchten_m;

  /// Fluid density at zero pressure
  Real _fluid_density0;

  /// Fluid bulk modulus
  Real _fluid_bulk_modulus;

  /// Fluid viscosity
  Real _fluid_viscosity;

  /// Fluid relative permeability type (FLAC or Corey)
  MooseEnum _relperm_type;

  /// Relative permeability exponent
  Real _relative_permeability_exponent;
};

#endif //POROUSFLOWUNSATURATEDBASE_H
