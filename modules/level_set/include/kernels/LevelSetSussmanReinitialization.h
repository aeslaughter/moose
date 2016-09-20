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

#ifndef LEVELSETSUSSMANREINITIALIZATION_H
#define LEVELSETSUSSMANREINITIALIZATION_H

// MOOSE includes
#include "Diffusion.h"
#include "Function.h"

// Forward declarations
class LevelSetSussmanReinitialization;

template<>
InputParameters validParams<LevelSetSussmanReinitialization>();

/**
 */
class LevelSetSussmanReinitialization :
  public Diffusion
{
public:

  /**
   */
  LevelSetSussmanReinitialization(const InputParameters & parameters);

protected:

  /**
   */
  virtual Real computeQpResidual() override;
  virtual Real computeQpJacobian() override;

  virtual Real sign();
  virtual Real dsign();


  const PostprocessorValue & _epsilon;
};

#endif // LEVELSETSUSSMANREINITIALIZATION_H
