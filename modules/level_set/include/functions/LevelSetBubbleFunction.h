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

#ifndef LEVELSETBUBBLEFUNCTION_H
#define LEVELSETBUBBLEFUNCTION_H

// MOOSE includes
#include "Function.h"

class LevelSetBubbleFunction;

template<>
InputParameters validParams<LevelSetBubbleFunction>();

class LevelSetBubbleFunction : public Function
{
public:

  LevelSetBubbleFunction(const InputParameters & parameters);

  virtual Real value(Real /*t*/, const Point & p) override;
  virtual RealGradient gradient(Real /*t*/, const Point & p) override;

protected:

  const RealVectorValue & _center;
  const Real & _radius;
  const Real & _epsilon;
};

#endif // LEVELSETBUBBLEFUNCTION_H
