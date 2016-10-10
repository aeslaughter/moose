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
#include "Diffusion.h"
#include "Function.h"

// Forward declarations
class LevelSetOlssonReinitialization;

template<>
InputParameters validParams<LevelSetOlssonReinitialization>();

/**
 */
class LevelSetOlssonReinitialization :
  public Diffusion
{
public:

  /**
   */
  LevelSetOlssonReinitialization(const InputParameters & parameters);

protected:

  /**
   */
  virtual Real computeQpResidual();
  virtual Real computeQpJacobian();
  virtual Real computeQpOffDiagJacobian(const unsigned int jvar);

  const VariableGradient & _grad_levelset_0;
  const Real & _epsilon;
  // For speed
  RealVectorValue _f;
  Real _s;
  RealVectorValue _n_hat;



};

#endif // LEVELSETOLSSONREINITIALIZATION_H
