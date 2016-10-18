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

#ifndef LEVELSETOLSSONVORTEX_H
#define LEVELSETOLSSONVORTEX_H

#include "Function.h"

// Forward declarations
class LevelSetOlssonVortex;

template<>
InputParameters validParams<LevelSetOlssonVortex>();

/**
 * Defines a vortex velocity field in the x-y plane.
 */
class LevelSetOlssonVortex : public Function
{
public:

  LevelSetOlssonVortex(const InputParameters & parameters);

  Real value(Real t, const Point & p) override;

  RealVectorValue vectorValue(Real t, const Point & p) override;

protected:

  /// Total time for the velocity field to complete reverse
  const Real & _reverse_time;

  /// Type of reverse (instantaneous or smooth)
  const MooseEnum & _reverse_type;

  /// The vector component to return
  const MooseEnum & _component;

  /// The velocity field computed
  RealVectorValue _output;

  /// The time reversal coefficient
  Real _reverse_coefficient;

  // Convenience for libMesh::pi
  const Real _pi;
};

#endif // LEVELSETOLSSONVORTEX_H
