//* This file is part of the MOOSE framework
//* https://www.mooseframework.org
//*
//* All rights reserved, see COPYRIGHT for full restrictions
//* https://github.com/idaholab/moose/blob/master/COPYRIGHT
//*
//* Licensed under LGPL 2.1, please see LICENSE for details
//* https://www.gnu.org/licenses/lgpl-2.1.html

// Moose includes
#include "SurrogateModelOutput.h"
#include "SurrogateModel.h"
#include "FEProblem.h"
#include "RestartableDataIO.h"
#include "RestartableData.h"

registerMooseObject("StochasticToolsApp", SurrogateModelOutput);

InputParameters
SurrogateModelOutput::validParams()
{
  InputParameters params = FileOutput::validParams();
  params.addClassDescription("Output for trained SurrogateModel data.");
  params.addRequiredParam<std::vector<UserObjectName>>(
      "surrogates", "A list of SurrogateModel objects to output.");
  return params;
}

SurrogateModelOutput::SurrogateModelOutput(const InputParameters & parameters)
  : FileOutput(parameters),
    SurrogateModelInterface(this),
    _surrogates(getParam<std::vector<UserObjectName>>("surrogates"))
{
}

void
SurrogateModelOutput::output(const ExecFlagType & /*type*/)
{
  if (processor_id() == 0)
  {
    RestartableDataIO restartable_data_io(_app);
    for (const auto & surrogate_name : _surrogates)
    {
      const SurrogateModel & model = getSurrogateModelByName(surrogate_name);
      const std::string filename =
        this->filename() + "_" + surrogate_name + restartable_data_io.getRestartableDataExt();

      const RestartableDataMap & meta_data = _app.getRestartableDataMap(model.name());
      restartable_data_io.writeRestartableData(filename, meta_data);

      std::cout << "WRITE:--------------------------------------------------------" << std::endl;

      auto coeff =
        static_cast<RestartableData<std::vector<Real>> *>(meta_data.at("_coeff").value.get());

      std::this_thread::sleep_for(std::chrono::seconds(2 * processor_id()));
      std::cerr << processor_id() << ": coeff->size() = " << coeff->get().size() << std::endl;
      std::cerr << "coeff = ";
      for (auto & val : coeff->get())
        std::cerr << val << " ";
      std::cerr << std::endl;

      std::this_thread::sleep_for(std::chrono::seconds(2 * processor_id()));
      auto tuple = static_cast<RestartableData<std::vector<std::vector<unsigned int>>> *>(
        meta_data.at("_tuple").value.get());
      std::cerr << processor_id() << ": tuple->size() = " << tuple->get().size() << std::endl;
      for (std::size_t i = 0; i < tuple->get().size(); ++i)
      {
        std::cerr << "tuple[" << i << "] = ";
        for (auto & val : tuple->get()[i])
          std::cerr << val << " ";
        std::cerr << std::endl;
      }
    }
  }
}
