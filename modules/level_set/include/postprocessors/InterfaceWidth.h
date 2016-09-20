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

#ifndef INTERFACEWIDTH_H
#define INTERFACEWIDTH_H

// MOOSE includes
#include "ElementPostprocessor.h"

// Forward declarations
class InterfaceWidth;

template<>
InputParameters validParams<InterfaceWidth>();

/**
 *
 */
class InterfaceWidth : public ElementPostprocessor
{
public:

  /**
   * Class constructor
   * @param name
   * @param parameters
   */
  InterfaceWidth(const InputParameters & parameters);

  void initialize();

  void execute();
  void finalize();
  void threadJoin(const UserObject & user_object);

  /**
   * Class destructor
   */
  virtual ~InterfaceWidth(){}

  /**
   *
   */
  virtual PostprocessorValue getValue();

private:
  Real _interface_width;
  unsigned int _level;
};

#endif // INTERFACEWIDTH_H
