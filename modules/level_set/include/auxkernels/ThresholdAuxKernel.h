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

#ifndef THRESHOLDAUXKERNEL_H
#define THRESHOLDAUXKERNEL_H

// MOOSE includes
#include "AuxKernel.h"

// Forward declerations
class ThresholdAuxKernel;

template<>
InputParameters validParams<ThresholdAuxKernel>();

/**
 *
 */
class ThresholdAuxKernel : public AuxKernel
{
public:

  /**
   * Class constructor
   * @param name
   */
  ThresholdAuxKernel(const InputParameters & parameters);

  /**
   * Class destructor
   */
  virtual ~ThresholdAuxKernel(){};

protected:

  /**
   *
   */
  virtual Real computeValue();

private:

  const VariableValue & _threshold_variable;
  Real _threshold;
  Real _above_value;
  Real _below_value;

//  bool(*_compare)(Real, Real);

};

#endif //THRESHOLDAUXKERNEL_H
