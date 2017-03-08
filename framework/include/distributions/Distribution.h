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

#ifndef DISTRIBUTION_H
#define DISTRIBUTION_H

#include "MooseObject.h"
#include "DistributionBase.h"
#include "SetupInterface.h"

class Distribution;

template<>
InputParameters validParams<Distribution>();

class Distribution :
  public MooseObject,
  public SetupInterface,
  public DistributionBase
{
public:
  Distribution(const InputParameters & parameters);
  virtual ~Distribution();
};

#endif /* DISTRIBUTION_H*/
