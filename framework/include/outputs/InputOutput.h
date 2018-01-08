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

#ifndef INPUTOUTPUT_H
#define INPUTOUTPUT_H

// MOOSE includes
#include "FileOutput.h"

class InputOutput;

template <>
InputParameters validParams<InputOutput>();

/**
 * Outputs complete MOOSE input file that includes all objects, including those added by actions.
 */
class InputOutput : public FileOutput
{
public:
  InputOutput(const InputParameters & parameters);
  virtual void output(const ExecFlagType & type) override;
  virtual std::string filename() override;

  static std::map<std::string, std::string> stringifyParameters(const InputParameters & parameters);

};

#endif
