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

#ifndef LEVELSETVORTEX_H
#define LEVELSETVORTEX_H

#include "Function.h"

// Forward declerations
class LevelSetVortex;

template<>
InputParameters validParams<LevelSetVortex>();

/**
 *
 */
class LevelSetVortex : public Function
{
public:

  /**
   * Class constructor
   * @param name
   * @param parameters
   */
  LevelSetVortex(const InputParameters & parameters);

  /**
   *
   */
  Real value(Real t, const Point & p) override;
  RealVectorValue vectorValue(Real t, const Point & p) override;

protected:
  const Real & _reverse_time;
  const MooseEnum & _component;

};

#endif // LEVELSETVORTEX_H
