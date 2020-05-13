//* This file is part of the MOOSE framework
//* https://www.mooseframework.org
//*
//* All rights reserved, see COPYRIGHT for full restrictions
//* https://github.com/idaholab/moose/blob/master/COPYRIGHT
//*
//* Licensed under LGPL 2.1, please see LICENSE for details
//* https://www.gnu.org/licenses/lgpl-2.1.html

#pragma once

// MOOSE includes
#include "MooseTypes.h"
#include "Restartable.h"
#include "VectorPostprocessorStorage.h"

// libMesh includes
#include "libmesh/parallel_object.h"

#include <unordered_map>

class FEProblemBase;

class VectorPostprocessorData : public Restartable, public libMesh::ParallelObject
{
public:
  using VectorPostprocessorState = VectorPostprocessorVectorState<Real>;
  static InputParameters validParams();

  /**
   * Class constructor
   */
  VectorPostprocessorData(FEProblemBase & fe_problem);

  /**
   * Initialization method, sets the current and old value to 0.0 for this postprocessor
   */
  void init(const std::string & name);

  /**
   * Initialization method, sets the current and old value to 0.0 for this
   * VectorPostprocessor
   *
   * @param vpp_name The name of the VectorPostprocessor
   * @param vector_name The name of the vector
   * @param contains_complete_history True if the vector will naturally contain the complete time
   * history of the values
   * @param is_broadcast True if the vector will already be replicated by the VPP.  This prevents
   * unnecessary broadcasting by MOOSE.
   */
  VectorPostprocessorValue & declareVector(const std::string & vpp_name,
                                           const std::string & vector_name,
                                           bool contains_complete_history,
                                           bool is_broadcast,
                                           bool is_distributed);

  /**
   * Returns a true value if the VectorPostprocessor exists
   */
  bool hasVectorPostprocessor(const std::string & name);

  /**
   * Return the value for the post processor
   * @param vpp_name The name of the VectorPostprocessor
   * @param vector_name The name of the vector
   * @param needs_broadcast Whether or not the vector needs to be broadcast
   * @return The reference to the current value
   */
  VectorPostprocessorValue & getVectorPostprocessorValue(const VectorPostprocessorName & vpp_name,
                                                         const std::string & vector_name,
                                                         bool needs_broadcast);

  /**
   * The the old value of an post-processor
   * @param vpp_name The name of the VectorPostprocessor
   * @param vector_name The name of the vector
   * @param needs_broadcast Whether or not the vector needs to be broadcast
   * @return The reference to the old value
   */
  VectorPostprocessorValue &
  getVectorPostprocessorValueOld(const VectorPostprocessorName & vpp_name,
                                 const std::string & vector_name,
                                 bool needs_broadcast);

  /**
   * Return the scatter value for the post processor
   * @param vpp_name The name of the VectorPostprocessor
   * @param vector_name The name of the vector
   * @return The reference to the current scatter value
   */
  ScatterVectorPostprocessorValue &
  getScatterVectorPostprocessorValue(const VectorPostprocessorName & vpp_name,
                                     const std::string & vector_name);

  /**
   * Return the scatter value for the post processor
   * @param vpp_name The name of the VectorPostprocessor
   * @param vector_name The name of the vector
   * @return The reference to the old scatter value
   */
  ScatterVectorPostprocessorValue &
  getScatterVectorPostprocessorValueOld(const VectorPostprocessorName & vpp_name,
                                        const std::string & vector_name);

  /**
   * Check to see if a VPP has any vectors at all
   */
  bool hasVectors(const std::string & vpp_name) const;

  /**
   * Returns a Boolean indicating whether the specified VPP vectors contain complete history.
   */
  bool containsCompleteHistory(const std::string & name) const;

  /**
   * Returns a Boolean indicating whether the specified VPP vectors are distributed
   */
  bool isDistributed(const std::string & name) const;

  /**
   * Get the map of vectors for a particular VectorPostprocessor
   * @param vpp_name The name of the VectorPostprocessor
   */
  const std::vector<std::pair<std::string, VectorPostprocessorVectorState<Real>>> &
  vectors(const std::string & vpp_name) const;

  /**
   * Broadcast and scatter vectors associated with vpp_name
   *
   * @param vpp_name The name of the vector to broadcast/scatter vectors for
   */
  void broadcastScatterVectors(const std::string & vpp_name);

  /**
   * Copy the current post-processor values into old (i.e. shift it "back in time") as needed
   */
  void copyValuesBack();

private:
  VectorPostprocessorState & getVectorPostprocessorHelper(const VectorPostprocessorName & vpp_name,
                                                          const std::string & vector_name,
                                                          bool get_current = true,
                                                          bool contains_complete_history = false,
                                                          bool is_broadcast = false,
                                                          bool is_distributed = false,
                                                          bool needs_broadcast = false,
                                                          bool needs_scatter = false);

  /// The VPP data store in a map: VPP Name to vector storage
  std::unordered_map<std::string, VectorPostprocessorStorage> _vpp_data;

  std::set<std::string> _requested_items;
  std::set<std::string> _supplied_items;
};
