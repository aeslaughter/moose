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

void callafunc(const std::function<void (const std::string &)> &t_func)
{
  t_func("bob");
}

template<>
InputParameters validParams<ChaiControlBase>()
{
  InputParameters params = validParams<Control>();
  return params;
}


ChaiControlBase::ChaiControlBase(const InputParameters & parameters) :
    Control(parameters)
{


}

void
ChaiControlBase::execute()
{
  chaiscript::ChaiScript chai(chaiscript::Std_Lib::library());

  //chaiscript::ChaiScript chai;

  int result = chai.eval<int>("1 + 3");

  std::cout << "result = " << result << std::endl;

  std::string result2 = chai.eval_file<std::string>("control.chai");

  std::cout << "result2 = " << result2 << std::endl;


//  chaiscript::ChaiScript chai;
//  chai.add(chaiscript::fun(&callafunc), "callafunc");
//  chai("callafunc(fun(x) { print(x); })"); // pass a lambda function to the registered function
                                           // which expects a typed std::function
//  std::function<void ()> f = chai.eval<std::function<void ()> >("dump_system");
//  f(); // call the ChaiScript function dump_system, from C++

}

#endif // LIBMESH_HAVE_CXX11
