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

#ifndef NORMALDISTRIBUTION_H
#define NORMALDISTRIBUTION_H

// STL includes
#include <random>
#include <cmath>

// MOOSE includes
#include "GeneralVectorPostprocessor.h"

// Forward Declarations
class NormalDistribution;

template<>
InputParameters validParams<NormalDistribution>();

class NormalDistribution : public GeneralVectorPostprocessor
{
public:
  NormalDistribution(const InputParameters & parameters);

  virtual void initialize() override;

  virtual void execute() override;


protected:

  Real sample();

  VectorPostprocessorValue & _value;

  const Real & _standard_deviation;
  const Real & _mean;
  const unsigned int & _count;

std::normal_distribution<> _distribution;


  std::random_device _random_device;
  std::mt19937 _generator;
};






#endif // NORMALDISTRIBUTION_H
