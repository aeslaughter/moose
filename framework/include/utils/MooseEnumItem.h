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

#ifndef MOOSEENUMITEM_H
#define MOOSEENUMITEM_H

// STL includes
#include <string>

class MooseApp;

/**
 * Class for containing MooseEnum item information.
 *
 * When using this class (or more likely the ExecFlagType alias) it is possible
 * to create an ExecFlagType without an ID. When this object is added to the
 * ExecFlagEnum object an ID will be assigned.
 */
class MooseEnumItem
{
public:
  static const int INVALID_ID;

  MooseEnumItem(const std::string & name);
  MooseEnumItem(const std::string & name, const int & id);
  MooseEnumItem(const MooseEnumItem & other);
  MooseEnumItem(MooseEnumItem && other) = default;
  MooseEnumItem & operator=(const MooseEnumItem & other);
  MooseEnumItem & operator=(MooseEnumItem && other) = default;
  ~MooseEnumItem() = default;

  ///@{
  /**
   * Return the numeric, name, or raw name.
   */
  const int & id() const { return _id; }
  const std::string & name() const { return _name; }
  const std::string & rawName() const { return _raw_name; }
  ///@}

  ///@{
  /**
   * Operator to allow this class to be used directly as a string for int.
   */
  operator int() const { return _id; }
  operator std::string() const { return _name; }
  ///@}

  ///@{
  /**
   * Comparison operators.
   *
   * The comparison operators using the char * and string are case sensitive.
   */
  bool operator==(const char * value) const;
  bool operator!=(const char * value) const;

  bool operator==(const std::string & value) const;
  bool operator!=(const std::string & value) const;

  bool operator==(int value) const { return _id == value; }
  bool operator!=(int value) const { return _id != value; }

  bool operator==(unsigned short value) const { return _id == value; }
  bool operator!=(unsigned short value) const { return _id != value; }

  bool operator==(const MooseEnumItem &) const;
  bool operator!=(const MooseEnumItem &) const;
  ///@}

  /**
   * Less than operator. This is required for this class to work in maps and sets.
   */
  bool operator<(const MooseEnumItem & other) const { return _id < other._id; }

  /**
   * ostream operator for string printing.
   */
  friend std::ostream & operator<<(std::ostream & out, const MooseEnumItem & item);

  // Allows the ID for ExecFlagType to be set automatically when it is registered, thus
  // allowing users to create flags without worrying about ID.
  friend MooseApp;

private:
  /// The name as provided in constructor
  std::string _raw_name;

  /// Upper case name
  std::string _name;

  /// The numeric value for item.
  mutable int _id; // mutable to allow MooseApp::registerExecFlag to set ID
};

#endif
