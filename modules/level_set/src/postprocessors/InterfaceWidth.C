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

#include "InterfaceWidth.h"

template<>
InputParameters validParams<InterfaceWidth>()
{
  InputParameters params = validParams<ElementPostprocessor>();
  params.addParam<unsigned int>("level", 0, "The refinement level to base computation of the interface width.");
  return params;
}

InterfaceWidth::InterfaceWidth(const InputParameters & parameters) :
    ElementPostprocessor(parameters),
    _interface_width(std::numeric_limits<Real>::max()),
    _level(getParam<unsigned int>("level"))
{
}

void
InterfaceWidth::initialize()
{
  _interface_width = std::numeric_limits<Real>::max();
}


void
InterfaceWidth::execute()
{
  int r = _current_elem->level() - _level;
  if (r >= 0)
    _interface_width = std::min(_interface_width, _current_elem->hmax()*std::pow(2, r));
}

void
InterfaceWidth::finalize()
{
  gatherMin(_interface_width);
}

void
InterfaceWidth::threadJoin(const UserObject & user_object)
{
  const InterfaceWidth & w = static_cast<const InterfaceWidth&>(user_object);
  _interface_width = std::min(_interface_width, w._interface_width);
}


PostprocessorValue
InterfaceWidth::getValue()
{
  return _interface_width;
}
