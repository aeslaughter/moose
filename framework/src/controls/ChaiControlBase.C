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


}

void
ChaiControlBase::execute()
{
  chaiscript::ChaiScript chai(chaiscript::Std_Lib::library());

  chai.eval("print(\"hello\");");


  try
  {
    chai.eval("2.3 + \"String\"");
  }
  catch (const chaiscript::exception::eval_error &e)
  {
    std::cout << "Error\n" << e.pretty_print() << '\n';
  }

  //chaiscript::ChaiScript chai;


  //int result = chai.eval<int>("1 + 3");
  //std::cout << "result = " << result << std::endl;
/*

  const PostprocessorValue & pp = getPostprocessorValueByName("coef");
  std::cout << "pp = " << pp << std::endl;


  chai.add(chaiscript::var(pp), "pp");

  chai.eval("print(p);");

*/



//  double val = chai.eval_file<double>("control.chai");

  // double val = chai.eval<double>("print(\"here\"); value();");
  //std::cout << "val = " << val << std::endl;

  //result = chai.eval<int>("def function(){ return 1; }; function();");


  //std::function<double ()> f = chai.eval<std::function<double ()> >("function");
  //std::cout << "result = " << f() << std::endl;

  //  result = chai.eval<int>("function();");
//  std::cout << "result = " << result << std::endl;


  //_value = 1;


//  chai.add(chaiscript::fun(&ChaiControlBase::getPostprocessorValueByName, this), "method");


//  chai.add(chaiscript::fun(&ChaiControlBase::test), "test");


//  int result = chai.eval<int>("1 + 3");

  //chai.eval_file("control.chai");

  /*
  try
  {
    chai.eval<int>("test()", chaiscript::exception_specification<const std::exception &>());
  }
  catch (const chaiscript::exception::eval_error &)
  {
    std::cout << "Error in script parsing / execution" << std::endl;
  }
  catch (const chaiscript::exception::bad_boxed_cast &)
  {
    std::cout << "Error unboxing return value" << std::endl;
  }
  catch (const std::exception &e)
  {
    std::cout << "Error explicitly thrown from script" << std::endl;

  }
  */

//  chai.eval("test();");


//  std::cout << "value = " << _value << std::endl;

//  std::cout << "result2 = " << result2 << std::endl;


//  chaiscript::ChaiScript chai;
//  chai.add(chaiscript::fun(&callafunc), "callafunc");
//  chai("callafunc(fun(x) { print(x); })"); // pass a lambda function to the registered function
                                           // which expects a typed std::function
//  std::function<void ()> f = chai.eval<std::function<void ()> >("dump_system");
//  f(); // call the ChaiScript function dump_system, from C++

}

#endif // LIBMESH_HAVE_CXX11
