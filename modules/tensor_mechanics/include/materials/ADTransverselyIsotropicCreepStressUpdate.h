//* This file is part of the MOOSE framework
//* https://www.mooseframework.org
//*
//* All rights reserved, see COPYRIGHT for full restrictions
//* https://github.com/idaholab/moose/blob/master/COPYRIGHT
//*
//* Licensed under LGPL 2.1, please see LICENSE for details
//* https://www.gnu.org/licenses/lgpl-2.1.html

#pragma once

#include "ADAnisotropicReturnCreepStressUpdateBase.h"

/**
 * This class uses the stress update material for an anisotropic creep
 * model.  This class is one of the basic radial return constitutive models; more complex
 * constitutive models combine creep and plasticity.
 *
 * This class inherits from AnisotropicReturnCreepStressUpdateBase and must be used
 * in conjunction with ComputeMultipleInelasticStress.  This class calculates
 * creep based on stress, temperature, and time effects.  This class also
 * computes the creep strain as a stateful material property.
 *
 * This class extends the usage of PowerLawCreep to transversely isotropic (i.e. anisotropic)
 * cases. For more information, consult, e.g. Stewart et al, "An anisotropic tertiary creep
 * damage constitutive model for anistropic materials", International Journal of Pressure Vessels
 * and Piping 88 (2011) 356--364.
 */

class ADTransverselyIsotropicCreepStressUpdate : public ADAnisotropicReturnCreepStressUpdateBase
{
public:
  static InputParameters validParams();

  ADTransverselyIsotropicCreepStressUpdate(const InputParameters & parameters);

  virtual Real
  computeStrainEnergyRateDensity(const ADMaterialProperty<RankTwoTensor> & stress,
                                 const ADMaterialProperty<RankTwoTensor> & strain_rate) override;

protected:
  virtual void computeStressInitialize(const ADDenseVector & effective_trial_stress,
                                       const ADRankFourTensor & elasticity_tensor) override;
  virtual ADReal computeResidual(const ADDenseVector & effective_trial_stress,
                                 const ADDenseVector & stress_new,
                                 const ADReal & scalar) override;
  virtual ADReal computeDerivative(const ADDenseVector & effective_trial_stress,
                                   const ADDenseVector & stress_new,
                                   const ADReal & scalar) override;

  virtual Real computeReferenceResidual(const ADDenseVector & effective_trial_stress,
                                        const ADDenseVector & stress_new,
                                        const ADReal & residual,
                                        const ADReal & scalar_effective_inelastic_strain) override;

  /**
   * Perform any necessary steps to finalize strain increment after return mapping iterations
   * @param inelasticStrainIncrement Inelastic strain increment
   * @param stress Cauchy stresss tensor
   * @param stress_dev Deviatoric partt of the Cauchy stresss tensor
   * @param delta_gamma Generalized radial return's plastic multiplier
   *
   */
  virtual void computeStrainFinalize(ADRankTwoTensor & inelasticStrainIncrement,
                                     const ADRankTwoTensor & stress,
                                     const ADDenseVector & stress_dev,
                                     const ADReal & delta_gamma) override;

  /**
   * Perform any necessary steps to finalize state after return mapping iterations
   * @param inelasticStrainIncrement Inelastic strain increment
   * @param delta_gamma Generalized radial return's plastic multiplier
   * @param stress Cauchy stresss tensor
   * @param stress_dev Deviatoric partt of the Cauchy stresss tensor

   */
  virtual void computeStressFinalize(const ADRankTwoTensor & inelasticStrainIncrement,
                                     const ADReal & delta_gamma,
                                     ADRankTwoTensor & stress,
                                     const ADDenseVector & stress_dev) override;

  /// Flag to determine if temperature is supplied by the user
  const bool _has_temp;

  /// Temperature variable value
  const VariableValue & _temperature;

  /// Leading coefficient
  const Real _coefficient;

  /// Exponent on the effective stress
  const Real _n_exponent;

  /// Exponent on time
  const Real _m_exponent;

  /// Activation energy for exp term
  const Real _activation_energy;

  /// Gas constant for exp term
  const Real _gas_constant;

  /// Simulation start time
  const Real _start_time;

  /// Exponential calculated from activation, gas constant, and temperature
  Real _exponential;

  /// Exponential calculated from current time
  Real _exp_time;

  /// Hill constants for orthotropic creep
  std::vector<Real> _hill_constants;

  /// Square of the q function for orthotropy
  ADReal _qsigma;
};
