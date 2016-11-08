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

#ifndef VECTORRECEIVER_H
#define VECTORRECEIVER_H

// STL includes
#include <random>
#include <cmath>

// MOOSE includes
#include "GeneralVectorPostprocessor.h"

// Forward Declarations
class VectorReceiver;

template<>
InputParameters validParams<VectorReceiver>();

class VectorReceiver : public GeneralVectorPostprocessor
{
public:
  VectorReceiver(const InputParameters & parameters);

  virtual void initialSetup() override;

  virtual void initialize() override {}
  virtual void execute() override {}
protected:

  VectorPostprocessorValue & _value;

  const Real & _default;
  const unsigned int & _count;

};

#endif // VECTORRECEIVER_H
