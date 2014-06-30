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

#include "PicardConsoleOutput.h"

template<>
InputParameters validParams<PicardConsoleOutput>()
{
  InputParameters params = validParams<TableOutput>();

#ifdef LIBMESH_HAVE_PETSC
  params.addParam<bool>("nonlinear_residuals", true, "Specifies whether output occurs on each nonlinear residual evaluation");
#endif

  return params;
}

PicardConsoleOutput::PicardConsoleOutput(const std::string & name, InputParameters parameters) :
  TableOutput(name, parameters)
{
}

PicardConsoleOutput::~PicardConsoleOutput()
{
}

void
PicardConsoleOutput::outputPostprocessors()
{
  TableOutput::outputPostprocessors();

  std::ostringstream oss;
  _postprocessor_table.printTable(oss);
  _console << oss.str() << std::endl;
}
