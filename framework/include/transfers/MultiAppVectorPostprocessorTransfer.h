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

#ifndef MULTIAPPVECTORPOSTPROCESSORTRANSFER_H
#define MULTIAPPVECTORPOSTPROCESSORTRANSFER_H

#include "MultiAppTransfer.h"

// Forward declarations
class MultiAppVectorPostprocessorTransfer;

template<>
InputParameters validParams<MultiAppVectorPostprocessorTransfer>();

/**
 * Copies the value of a Postprocessor from the Master to a MultiApp.
 */
class MultiAppVectorPostprocessorTransfer :
    public MultiAppTransfer
{
public:
  MultiAppVectorPostprocessorTransfer(const InputParameters & parameters);

  virtual void execute() override;

protected:

  void transfer(FEProblem & master_problem, FEProblem & sub_problem, unsigned int app_numc);


  PostprocessorName _pp_name;

  VectorPostprocessorName _vector_pp_name;

  std::string _vector_pp_vector_name;
};

#endif /* MULTIAPPPOSTPROCESSORTRANSFER_H */
