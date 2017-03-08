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
#ifndef DISTRIBUTIONVALUEPOSTPROCESSOR_H
#define DISTRIBUTIONVALUEPOSTPROCESSOR_H

#include "GeneralPostprocessor.h"

class DistributionValuePostprocessor;
class Distribution;

template<>
InputParameters validParams<DistributionValuePostprocessor>();

/**
 * This postprocessor is used to test the distribution capabilities.
 */
class DistributionValuePostprocessor : public GeneralPostprocessor
{
public:
  DistributionValuePostprocessor(const InputParameters & parameters);

  virtual void initialize() override;
  virtual void execute() override;
  virtual PostprocessorValue getValue() override;

protected:
  Distribution & _distribution;
  const Real & _cdf_value;
  const Real _sample_value;
};

#endif /* DISTRIBUTIONVALUEPOSTPROCESSOR_H */
