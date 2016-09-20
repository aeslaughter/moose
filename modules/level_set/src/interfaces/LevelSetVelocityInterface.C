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

// MOOSE includes
#include "LevelSetVelocityInterface.h"

template<>
InputParameters
validParams<LevelSetVelocityInterface<> >()
{
  InputParameters parameters = emptyInputParameters();
  parameters.addCoupledVar("velocity_x", 0, "The variable containing the x-component of the velocity front.");
  parameters.addCoupledVar("velocity_y", 0, "The variable containing the y-component of the velocity front.");
  parameters.addCoupledVar("velocity_z", 0, "The variable containing the z-component of the velocity front.");
  return parameters;
}
