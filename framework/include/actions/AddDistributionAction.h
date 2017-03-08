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

#ifndef ADDDISTRIBUTIONACTION_H
#define ADDDISTRIBUTIONACTION_H

#include "MooseObjectAction.h"

class AddDistributionAction;

template<>
InputParameters validParams<AddDistributionAction>();


/**
 * This class parses distributions in the [Distributions] block and creates them.
 */
class AddDistributionAction : public MooseObjectAction
{
public:
  AddDistributionAction(InputParameters params);

  virtual void act() override;
};

#endif /* ADDDISTRIBUTIONACTION_H */
