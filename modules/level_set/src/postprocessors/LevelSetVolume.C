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

#include "LevelSetVolume.h"

template<>
InputParameters validParams<LevelSetVolume>()
{
  InputParameters params = validParams<ElementVariablePostprocessor>();
  params.addParam<Real>("threshold", 0.0, "The level set threshold to consider for computing area/volume.");

  MooseEnum loc("inside=0 outside=1", "inside");
  params.addParam<MooseEnum>("location", loc, "The location of the area/volume to be computed.");
  return params;
}

LevelSetVolume::LevelSetVolume(const InputParameters & parameters) :
    ElementVariablePostprocessor(parameters),
    _threshold(getParam<Real>("threshold")),
    _inside(getParam<MooseEnum>("location") == "inside")
{
}

void
LevelSetVolume::initialize()
{
  _volume = 0;
}

void
LevelSetVolume::execute()
{
  Real cnt = 0;
  Real n = _u.size();

  // Perform the check for inside/outside outside the qp loop for speed
  if (_inside)
  {
    for (_qp = 0; _qp < n; ++_qp)
    if (_u[_qp] <= _threshold)
      cnt++;
  }
  else
  {
    for (_qp = 0; _qp < n; ++_qp)
    if (_u[_qp] > _threshold)
      cnt++;
  }
  _volume += cnt/n * _current_elem_volume;
}

void
LevelSetVolume::finalize()
{
  gatherSum(_volume);
}


Real
LevelSetVolume::getValue()
{
  return _volume;
}

void
LevelSetVolume::threadJoin(const UserObject & y)
{
  const LevelSetVolume & pps = static_cast<const LevelSetVolume &>(y);
  _volume += pps._volume;
}
