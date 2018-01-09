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
#include "MooseApp.h"

// hit
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

  /**
   * Add a system level node.
   * @param name The name of the sub-block to create and added objects shall be added.
   */
  hit::Node * addSystem(const std::string & name, hit::Node * parent);

  template<class T>
  hit::Node * addSystem(const std::string & name, hit::Node * parent);//, const std::string & action_name);


  /**
   * Adds a system level node as well as the subobjects from the supplied warehouse.
   *
   * @param name The name of the sub-block to create and added objects shall be added.
   * @param parent The parent node for containing the blocks.
   * @param warehouse The objects to add.
   */
  template<class T>
  hit::Node * addSystem(const std::string & name, hit::Node * parent, const MooseObjectWarehouseBase<T> & warehouse);

  /**
   * Adds subobjects from the supplied warehouse.
   *
   * @param parent The parent node for containing the blocks.
   * @param warehouse The objects to add.
   * @param comment (optional) String comment to place inline prior to the block.
   */
  template<class T>
  void addObjects(hit::Node * parent, const MooseObjectWarehouseBase<T> & warehouse);

  /**
   * Adds parameter key-value pairs to to the supplied parent object.
   *
   * Parameters are only added if they are valid and not private.
   * @param name The name of the parameter to add.
   * @param value The Value * containing the parameter value.
   * @param parent The parent hit node to contain the parameter.
   * @param parameters The InputParameters object for checking private/valid state.
   */
  void addParameterNode(const std::string & name, libMesh::Parameters::Value * value, hit::Node * parent, const InputParameters & parameters);

};


template<class T>
hit::Node *
InputOutput::addSystem(const std::string & name, hit::Node * parent)//, const std::string & action_name)
{
  std::vector<const T *> actions = _app.actionWarehouse().template getActions<T>();
  if (!actions.empty())
  {
    hit::Node * node = addSystem(name, parent);
    for (const auto action_ptr : actions)
      for (const auto & map_pair : action_ptr->parameters())
        addParameterNode(map_pair.first, map_pair.second, node, action_ptr->parameters());
    return node;
  }
  return nullptr;
}


template<class T>
hit::Node *
InputOutput::addSystem(const std::string & name, hit::Node * parent, const MooseObjectWarehouseBase<T> & warehouse)
{
  if (warehouse.hasObjects())
  {
    hit::Node * node = addSystem(name, parent);
    addObjects(node, warehouse);
    return node;
  }
  return nullptr;
}

template<class T>
void
InputOutput::addObjects(hit::Node * parent, const MooseObjectWarehouseBase<T> & warehouse)
{
  const std::vector<std::shared_ptr<T>> & objects = warehouse.getObjects();
  for (const std::shared_ptr<T> & object_ptr : objects)
  {
    hit::Section * sub_section = new hit::Section(object_ptr->name());
    parent->addChild(sub_section);
    for (const auto & map_pair : object_ptr->parameters())
      addParameterNode(map_pair.first, map_pair.second, sub_section, object_ptr->parameters());
  }
}

#endif
