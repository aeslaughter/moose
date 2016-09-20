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

#ifndef LEVELSETVALUEMARKER_H
#define LEVELSETVALUEMARKER_H

// MOOSE includes
#include "ValueRangeMarker.h"
#include "LevelSetVelocityInterface.h"

// Forward declerations
class LevelSetValueMarker;

template<>
InputParameters validParams<LevelSetValueMarker>();

/**
 * A marker that tracks the level set variable and increases the bounding values
 * in the direction of the level set velocity front.
 */
class LevelSetValueMarker : public LevelSetVelocityInterface<ValueRangeMarker>
{
public:

  /**
   * Class constructor
   * @param name
   * @param parameters
   */
  LevelSetValueMarker(const InputParameters & parameters);

  /**
   * Class destructor
   */
  virtual ~LevelSetValueMarker(){}

protected:

  /**
   * Perform the marker calculation that adjusts the bounds in the direction of velocity
   */
  virtual MarkerValue computeQpMarker();

private:

  ///@{
  /// Upper/lower bounds from the input file
  const Real & _input_upper_bound;
  const Real & _input_lower_bound;
  ///@}

  /// Scaling factor to apply to bound in the direction of the velocity
  const Real & _bound_scale;

  /// Gradient of the levelset variable
  const VariableGradient & _grad_levelset_var;

  ///@{
  /// Member variables used to reduce the instatiating inside computeQpMarker
  RealVectorValue _n_hat;
  Real _v_dot_n;
  bool _inside;
  ///@}
};

#endif //LEVELSETVALUEMARKER_H
