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

#ifndef LEVELSETADVECTION_H
#define LEVELSETADVECTION_H

// MOOSE includes
#include "Kernel.h"
#include "Function.h"
#include "LevelSetVelocityInterface.h"

// Forward declarations
class LevelSetAdvection;

template<>
InputParameters validParams<LevelSetAdvection>();

/**
 * Advection Kernel for the levelset equation.
 *
 * \Psi_i \vec{v} \nabla u,
 * where \vec{v} is the interface velocity that is a set of
 * coupled variables.
 */
class LevelSetAdvection :
  public LevelSetVelocityInterface<Kernel>
{
public:

  LevelSetAdvection(const InputParameters & parameters);

protected:

  virtual Real computeQpResidual() override;

  virtual Real computeQpJacobian() override;
};

#endif //LEVELSETADVECTION_H
