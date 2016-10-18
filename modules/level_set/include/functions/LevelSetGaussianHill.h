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

#ifndef GAUSSIANHILL_H
#define GAUSSIANHILL_H

#include "Function.h"

// Forward declarations
class LevelSetGaussianHill;

template<>
InputParameters validParams<LevelSetGaussianHill>();

/**
 *
 */
class LevelSetGaussianHill : public Function
{
public:

  /**
   * Class constructor
   * @param name
   * @param parameters
   */
  LevelSetGaussianHill(const InputParameters & parameters);

  /**
   *
   */
  Real value(Real t, const Point & p);

protected:
  Real _sigma;
  std::vector<Real> _center;

  RealVectorValue _x_bar;


};

#endif //GAUSSIANHILL_H
