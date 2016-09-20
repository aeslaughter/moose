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

#ifndef LEVELSETADVECTIONSUPG_H
#define LEVELSETADVECTIONSUPG_H

// MOOSE includes
#include "TimeDerivative.h"
#include "LevelSetVelocityInterface.h"

// Forward declarations
class LevelSetAdvectionSUPG;

template<>
InputParameters validParams<LevelSetAdvectionSUPG>();

/**
 *
 */
class LevelSetAdvectionSUPG : public LevelSetVelocityInterface<Kernel>
{
public:

  /**
   * Class constructor
   * @param name
   * @param parameters
   */
  LevelSetAdvectionSUPG(const InputParameters & parameters);


protected:
  Real computeQpResidual();
  Real computeQpJacobian();
};

#endif //LEVELSETADVECTIONSUPG_H
