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

#include "LevelSetVortex.h"

template<>
InputParameters validParams<LevelSetVortex>()
{
  MooseEnum comp("x=0 y=1 z=2");

  InputParameters params = validParams<Function>();
  params.addParam<Real>("reverse_time", 8, "Total time for vortex reverse.");
  params.addRequiredParam<MooseEnum>("component", comp, "The component of velocity to return.");
  return params;
}

LevelSetVortex::LevelSetVortex(const InputParameters & parameters) :
  Function(parameters),
  _reverse_time(getParam<Real>("reverse_time")),
  _component(getParam<MooseEnum>("component"))
{
}

Real
LevelSetVortex::value(Real t, const Point & p)
{
  return vectorValue(t, p)(_component);
}

RealVectorValue
LevelSetVortex::vectorValue(Real t, const Point & p)
{
  RealVectorValue output;
  if (t > _reverse_time)
  {
    output(0) = sin(libMesh::pi * p(0)) * sin(libMesh::pi * p(0)) * sin(2*libMesh::pi*p(1));
    output(1) = -sin(libMesh::pi * p(1)) * sin(libMesh::pi * p(1)) * sin(2*libMesh::pi*p(0));
  }
  else
  {
    output(0) = -sin(libMesh::pi * p(0)) * sin(libMesh::pi * p(0)) * sin(2*libMesh::pi*p(1));
    output(1) = sin(libMesh::pi * p(1)) * sin(libMesh::pi * p(1)) * sin(2*libMesh::pi*p(0));
  }

  return output;
}
