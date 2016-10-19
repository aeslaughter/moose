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

#ifndef LEVELSETOLSSONREINITIALIZATION_H
#define LEVELSETOLSSONREINITIALIZATION_H

// MOOSE includes
#include "Kernel.h"
#include "Function.h"

// Forward declarations
class LevelSetOlssonReinitialization;

template<>
InputParameters validParams<LevelSetOlssonReinitialization>();

/**
 * Implements the re-initialization equation proposed by Olsson et. al. (2007).
 */
class LevelSetOlssonReinitialization :
  public Kernel
{
public:

  LevelSetOlssonReinitialization(const InputParameters & parameters);

protected:

  virtual Real computeQpResidual() override;

  virtual Real computeQpJacobian() override;

  /// Gradient of the level set variable at time, \tau = 0.
  const VariableGradient & _grad_levelset_0;

  /// Interface thickness
  const PostprocessorValue & _epsilon;

  ///@{
  /// Helper members to avoid initializing variables in computeQpResidual/Jacobian
  RealVectorValue _f;
  Real _s;
  RealVectorValue _n_hat;
  ///@}
};

#endif // LEVELSETOLSSONREINITIALIZATION_H
