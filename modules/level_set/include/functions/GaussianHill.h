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

// Forward declerations
class GaussianHill;

template<>
InputParameters validParams<GaussianHill>();

/**
 *
 */
class GaussianHill : public Function
{
public:

  /**
   * Class constructor
   * @param name
   * @param parameters
   */
  GaussianHill(const InputParameters & parameters);

  /**
   *
   */
  Real value(Real t, const Point & p);

protected:
  Real _sigma;
  std::vector<Real> _center;

};

#endif //GAUSSIANHILL_H
