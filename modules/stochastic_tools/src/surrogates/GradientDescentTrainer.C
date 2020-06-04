//* This file is part of the MOOSE framework
//* https://www.mooseframework.org
//*
//* All rights reserved, see COPYRIGHT for full restrictions
//* https://github.com/idaholab/moose/blob/master/COPYRIGHT
//*
//* Licensed under LGPL 2.1, please see LICENSE for details
//* https://www.gnu.org/licenses/lgpl-2.1.html

#include "GradientDescentTrainer.h"
#include "Sampler.h"
#include "DenseMatrix.h"
#include "MooseRandom.h"

registerMooseObject("StochasticToolsApp", PolynomialLeastSquares);
registerMooseObject("StochasticToolsApp", GradientDescentTrainer);

InputParameters
ObjectiveFunction::validParams()
{
  InputParameters params = GeneralUserObject::validParams();
  return params;
}

ObjectiveFunction::ObjectiveFunction(const InputParameters & parameters):
    GeneralUserObject(parameters)
{
}


InputParameters
PolynomialLeastSquares::validParams()
{
  InputParameters params = ObjectiveFunction::validParams();
  params.addParam<unsigned int>("order", 1, "The polynomial order to compute.");
  params.addRequiredParam<VectorPostprocessorName>("vector_postprocessor", "The name of the VectorPostprocessor object containing the training data.");
  params.addRequiredParam<std::string>("x_vector", "The name of the vector containing the x training data.");
  params.addRequiredParam<std::string>("y_vector", "The name of the vector containing the y training data.");
  return params;
}

PolynomialLeastSquares::PolynomialLeastSquares(const InputParameters & parameters) :
    ObjectiveFunction(parameters),
    _order(getParam<unsigned int>("order")),
    _x_training_data(getVectorPostprocessorValue("vector_postprocessor", getParam<std::string>("x_vector"), false)),
    _y_training_data(getVectorPostprocessorValue("vector_postprocessor", getParam<std::string>("y_vector"), false))
{
}

void
PolynomialLeastSquares::initialSetup()
{
  std::cout << "PolynomialLeastSquares::initialSetup" << std::endl;


}

unsigned int
PolynomialLeastSquares::size() const
{
  return _order + 1;
}


Real
PolynomialLeastSquares::value(const DenseVector<Real> & /*x*/) const
{
  // TODO: Create a model to use this function and an AD version that computes the gradient automatically
  // However, to use this object you don't need the training data. So, perhaps there just needs to
  // be a PolynomialModel object that can accept the DenseVector values

  return 0.0;
}


DenseVector<Real>
PolynomialLeastSquares::gradient(const DenseVector<Real> & x) const
{
  // There is more Order of operation stuff between VPP and UO. In practice the ObjectFunctions
  // can be created late via an action, for now hack it in
  if (_b_vector.size() == 0)
  {
    _A_matrix.resize(_x_training_data.size(), _order+1);
    _b_vector = _y_training_data;
    _Ax_minus_b.resize(_y_training_data.size());

    // TODO: Loop over offsets and to a std::fill using _A.get_values() on the underlying std::vector
    for (unsigned int col = 0; col < _order+1; ++col)
      for (unsigned int row = 0; row < _A_matrix.m(); ++row)
        _A_matrix(row, col) = std::pow(_x_training_data[row], col);
  }


  //const VectorPostprocessorValue & x_train = getVectorPostprocessorValueByName("old_faithful", "duration", false);
  //const VectorPostprocessorValue & y_train = getVectorPostprocessorValueByName("old_faithful", "wait", false);
  /*

  DenseMatrix<Real> A(x_train.size(), 2);
  for (unsigned int i = 0; i < A.m(); ++i)
  {
    A(i,0) = 1;
    A(i,1) = x_train[i];
  }

  DenseVector<Real> b(y_train);
  */

  _A_matrix.vector_mult(_Ax_minus_b, x);
  _Ax_minus_b -= _b_vector;


  /*
  DenseVector<Real> Ax_b = y_train;


  std::cout << A.m() << " " << A.n() << std::endl;
  std::cout << x.size() << std::endl;
  std::cout << Ax_b.size() << std::endl;

  A.vector_mult_add(Ax_b, -1, x);

  */

//A^T(Ax-b)
  //DenseMatrix<Real> AT;
  //A.get_transpose(AT);
  //DenseVector<Real> inner;
  //A.vector_mult(inner, x);
  //inner -= b;

  DenseVector<Real> x_out;
  _A_matrix.vector_mult_transpose(x_out, _Ax_minus_b);
  return x_out;
}




InputParameters
GradientDescentTrainer::validParams()
{
  InputParameters params = SurrogateTrainer::validParams();
  params.addRequiredParam<UserObjectName>("objective_function", "The objective function to minimize.");
  params.addRequiredParam<unsigned int>("max_iterations", "The maximum number of iterations to perform.");
  params.addRequiredParam<Real>("step_size", "The gradient descent step size.");
  return params;
}

GradientDescentTrainer::GradientDescentTrainer(const InputParameters & parameters)
    : SurrogateTrainer(parameters),
      _objective_function(getUserObject<ObjectiveFunction>("objective_function")),
      _max_iterations(getParam<unsigned int>("max_iterations")),
      _step_size(getParam<Real>("step_size")),
      _function_values(declareModelData<DenseVector<Real>>("function_values"))
{
}

void
GradientDescentTrainer::initialSetup()
{
  // _sampler_ptr = &getSampler("A");
}

void
GradientDescentTrainer::initialize()
{
}

void
GradientDescentTrainer::execute()
{
  // Support tolerance based iterations, stop after some relative tolerance change
  // Add StepSize objects
  // Add regulizer object
  // Add Initialize guess object


  //const std::size_t maxiter = 10000;
  //const Real step_size =  0.00001;
  //CostFunction func;

  /*

  const DenseMatrix<Real> A = _sampler_ptr->getGlobalSamples();
  DenseVector<Real> xtrue(std::vector<Real>({0, 1}));
  DenseVector<Real> b;//(xtrue.size());
  A.vector_mult(b, xtrue);

  unsigned int n = 60;//A.size();

  for (unsigned int i = 0; i < n; ++i)
    b(i) = b(i) + 0.01 * MooseRandom::randNormal(0, 1);
 */

  const auto n = _objective_function.size();
  _function_values.resize(n);
  for (std::size_t i = 0; i < _max_iterations; ++i)
  {
    DenseVector<Real> out = _objective_function.gradient(_function_values);
    out.scale(_step_size);
    _function_values -= out;
  }

  std::cout << "x = " << _function_values << std::endl;

}

void
GradientDescentTrainer::finalize()
{
}
