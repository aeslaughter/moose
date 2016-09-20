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

#ifndef LEVELSETVARIABLENORMALAUXKERNEL_H
#define LEVELSETVARIABLENORMALAUXKERNEL_H

// MOOSE includes
#include "AuxKernel.h"

// Forward declerations
class LevelSetVariableNormalAuxKernel;

template<>
InputParameters validParams<LevelSetVariableNormalAuxKernel>();

/**
 *
 */
class LevelSetVariableNormalAuxKernel : public AuxKernel
{
public:

  /**
   * Class constructor
   * @param name
   */
  LevelSetVariableNormalAuxKernel(const InputParameters & parameters);

protected:

  /**
   *
   */
  virtual Real computeValue();

private:

  const VariableGradient & _grad_levelset_variable;

  const MooseEnum & _component;

};

#endif //LEVELSETVARIABLENORMALAUXKERNEL_H
