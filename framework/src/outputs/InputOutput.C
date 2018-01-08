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
#include "InputOutput.h"

template <>
InputParameters
validParams<InputOutput>()
{
  InputParameters params = validParams<FileOutput>();
  params.set<ExecFlagEnum>("execute_on") = EXEC_INITIAL;
  return params;
}

InputOutput::InputOutput(const InputParameters & parameters) : FileOutput(parameters) {}

std::string
InputOutput::filename()
{
  return _file_base + ".i";
}

void
InputOutput::output(const ExecFlagType & /*type*/)
{
  std::cout << "HERE" << std::endl;
}
