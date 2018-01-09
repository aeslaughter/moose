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

// libMesh includes
#include "libmesh/parameters.h"

// MOOSE includes
#include "FileOutput.h"
#include "MooseObjectWarehouseBase.h"
#include "parse.h"

class InputOutput;
//class MooseObjectWarehouseBase;

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

protected:
  //static std::map<std::string, std::string> stringifyParameters(const InputParameters & parameters);

  void addParameterNodes(const std::string & name, libMesh::Parameters::Value * value, hit::Node * parent, const InputParameters & parameters);

  template<class T>
  void addSubSectionNodes(const std::string & name, const MooseObjectWarehouseBase<T> & warehouse, hit::Node * parent);
};

template<class T>
void InputOutput::addSubSectionNodes(const std::string & name, const MooseObjectWarehouseBase<T> & warehouse, hit::Node * parent)
{
  hit::Section * node = new hit::Section(name);
  parent->addChild(node);

  const std::vector<std::shared_ptr<T>> & objects = warehouse.getObjects();
  for (const std::shared_ptr<T> & object_ptr : objects)
  {
    hit::Section * sub_section = new hit::Section(object_ptr->name());
    node->addChild(sub_section);
    for (const auto & map_pair : object_ptr->parameters())
      addParameterNodes(map_pair.first, map_pair.second, sub_section, object_ptr->parameters());
  }
}

#endif
