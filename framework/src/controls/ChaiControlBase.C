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
#include "ChaiControlBase.h"

// ChaiScript requires Cxx11
#ifdef LIBMESH_HAVE_CXX11


template<>
InputParameters validParams<ChaiControlBase>()
{
  InputParameters params = validParams<Control>();
  return params;
}


ChaiControlBase::ChaiControlBase(const InputParameters & parameters) :
    Control(parameters)
{

  chaiscript::ChaiScript chai(chaiscript::Std_Lib::library());

}

void
ChaiControlBase::execute()
{



  std::cout << "test" << std::endl;

}

#endif // LIBMESH_HAVE_CXX11
