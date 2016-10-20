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
#include "Kernel.h"
#include "LevelSetVelocityInterface.h"

// Forward declarations
class LevelSetAdvectionSUPG;

template<>
InputParameters validParams<LevelSetAdvectionSUPG>();

/**
 * SUPG stablization for the advection portion of the level set equation.
 */
class LevelSetAdvectionSUPG : public LevelSetVelocityInterface<Kernel>
{
public:

  LevelSetAdvectionSUPG(const InputParameters & parameters);


protected:
  Real computeQpResidual() override;

  Real computeQpJacobian() override;
};

#endif //LEVELSETADVECTIONSUPG_H
