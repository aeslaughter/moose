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

#ifndef LEVELSETTIMEDERIVATIVESUPG_H
#define LEVELSETTIMEDERIVATIVESUPG_H

// MOOSE includes
#include "TimeDerivative.h"
#include "LevelSetVelocityInterface.h"

// Forward declarations
class LevelSetTimeDerivativeSUPG;

template<>
InputParameters validParams<LevelSetTimeDerivativeSUPG>();

/**
 *
 */
class LevelSetTimeDerivativeSUPG : public LevelSetVelocityInterface<TimeDerivative>
{
public:

  /**
   * Class constructor
   * @param name
   * @param parameters
   */
  LevelSetTimeDerivativeSUPG(const InputParameters & parameters);


protected:
  Real computeQpResidual();
  Real computeQpJacobian();
};

#endif //LEVELSETTIMEDERIVATIVESUPG_H
