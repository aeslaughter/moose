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
#include "MultiAppVectorPostprocessorTransfer.h"
#include "Sampler.h"

// Forward declarations
class SamplerPostprocessorTransfer;
class SamplerReceiver;
class SamplerFullSolveMultiApp;
class StochasticResults;

template <>
InputParameters validParams<SamplerPostprocessorTransfer>();

/**
 * Transfer Postprocessor from sub-applications to the master application.
 */
class SamplerPostprocessorTransfer : public MultiAppVectorPostprocessorTransfer
{
public:
  SamplerPostprocessorTransfer(const InputParameters & parameters);
  virtual void initialSetup() override;

protected:
  virtual void executeFromMultiapp() override;

  /// Sampler object that is retrieved from the SamplerTransientMultiApp or SamplerFullSolveMultiApp
  Sampler * _sampler;

  /// Storage for StochasticResults object that data will be transferred to/from
  StochasticResults * _results;

  /// Local values of compute PP values
  std::vector<PostprocessorValue> _local_values;

  /// SamplerFullSolveMultiapp batch mode flag
  bool _batch_mode = false;

private:

  ///@{
  /** Helper methods for performing transfer in various modes, see SamplerFullSolveMultiApp */
  void executeFromMultiappBatch();
  void executeFromMultiappNormal();
  ///@}
};
