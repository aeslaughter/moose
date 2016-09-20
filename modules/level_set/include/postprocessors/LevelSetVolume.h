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

#ifndef LEVELSETVOLUME_H
#define LEVELSETVOLUME_H

// MOOSE includes
#include "ElementVariablePostprocessor.h"

// Forward declerations
class LevelSetVolume;

template<>
InputParameters validParams<LevelSetVolume>();

/**
 *
 */
class LevelSetVolume : public ElementVariablePostprocessor
{
public:

  /**
   * Class constructor
   * @param name
   * @param parameters
   */
  LevelSetVolume(const InputParameters & parameters);


  virtual void initialize();
  virtual void finalize();
  virtual void execute();
  virtual Real getValue();
  virtual void threadJoin(const UserObject & y);
  virtual void computeQpValue(){};

protected:
  Real _volume;

  const Real & _threshold;
  const bool _inside;

};

#endif //LEVELSETVOLUME_H
