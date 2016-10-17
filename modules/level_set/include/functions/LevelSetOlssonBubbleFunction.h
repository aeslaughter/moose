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

#ifndef LEVELSETOLSSONBUBBLEFUNCTION_H
#define LEVELSETOLSSONBUBBLEFUNCTION_H

// MOOSE includes
#include "Function.h"

class LevelSetOlssonBubbleFunction;

template<>
InputParameters validParams<LevelSetOlssonBubbleFunction>();

/**
 * Implements the "bubble" function from Olsson and Kreiss (2005) that
 * creates function that varies from 0 to 1.
 */
class LevelSetOlssonBubbleFunction : public Function
{
public:

  LevelSetOlssonBubbleFunction(const InputParameters & parameters);

  virtual Real value(Real /*t*/, const Point & p) override;

  virtual RealGradient gradient(Real /*t*/, const Point & p) override;

protected:

  /// The 'center' of the bubble
  const RealVectorValue & _center;

  /// The radius of the bubble
  const Real & _radius;

  /// The interface thickness
  const Real & _epsilon;
};

#endif // LEVELSETOLSSONBUBBLEFUNCTION_H
