#include "LevelSetApp.h"
#include "Moose.h"
#include "AppFactory.h"
#include "MooseSyntax.h"

// InitialConditions

// Kernels
#include "LevelSetAdvection.h"
#include "LevelSetAdvectionSUPG.h"
#include "LevelSetTimeDerivativeSUPG.h"
#include "LevelSetOlssonReinitialization.h"

// AuxKernels
#include "ThresholdAuxKernel.h"
#include "LevelSetVariableNormalAuxKernel.h"

// Functions
#include "GaussianHill.h"
#include "LevelSetBubbleFunction.h"
#include "LevelSetVortex.h"

// Postprocessors
#include "CFLCondition.h"
#include "InterfaceWidth.h"
#include "LevelSetVolume.h"
#include "LevelSetOlssonTerminator.h"

// UserObjects
#include "LevelSetMeshRefinementTracker.h"

// Markers
#include "LevelSetValueMarker.h"

// Actions
#include "AddLevelSetKernels.h"
#include "AddLevelSetPostprocessors.h"

// Problems
#include "LevelSetProblem.h"
#include "LevelSetReinitializationProblem.h"

// MultiApps
#include "LevelSetReinitializationMultiApp.h"

// Transfers
#include "LevelSetMeshRefinementTransfer.h"

// Apps
#include "LevelSetReinitializationApp.h"

template<>
InputParameters validParams<LevelSetApp>()
{
  InputParameters params = validParams<MooseApp>();
  return params;
}

LevelSetApp::LevelSetApp(InputParameters parameters) :
    MooseApp(parameters)
{
  srand(processor_id());

  Moose::registerObjects(_factory);
  LevelSetApp::registerObjects(_factory);

  Moose::associateSyntax(_syntax, _action_factory);
  LevelSetApp::associateSyntax(_syntax, _action_factory);
}

void
LevelSetApp::registerApps()
{
  registerApp(LevelSetApp);
  registerApp(LevelSetReinitializationApp);
}

void
LevelSetApp::registerObjects(Factory & factory)
{
  // InitialConditions

  // Kernels
  registerKernel(LevelSetAdvection);
  registerKernel(LevelSetAdvectionSUPG);
  registerKernel(LevelSetTimeDerivativeSUPG);
  registerKernel(LevelSetOlssonReinitialization);

  // AuxKernels
  registerAuxKernel(ThresholdAuxKernel);
  registerAuxKernel(LevelSetVariableNormalAuxKernel);

  // Functions
  registerFunction(GaussianHill);
  registerFunction(LevelSetBubbleFunction);
  registerFunction(LevelSetVortex);

  // Postprocessors
  registerPostprocessor(CFLCondition);
  registerPostprocessor(InterfaceWidth);
  registerPostprocessor(LevelSetVolume);
  registerPostprocessor(LevelSetOlssonTerminator);

  // UserObjects
  registerUserObject(LevelSetMeshRefinementTracker);

  // Problems
  registerProblem(LevelSetProblem);
  registerProblem(LevelSetReinitializationProblem);

  // Markers
  registerMarker(LevelSetValueMarker);

  // MultiApps
  registerMultiApp(LevelSetReinitializationMultiApp);

  // Transfers
  registerTransfer(LevelSetMeshRefinementTransfer);
}

void
LevelSetApp::associateSyntax(Syntax & syntax, ActionFactory & action_factory)
{
  // level set kernel creation
  registerTask("add_level_set_kernels", false);
  registerAction(AddLevelSetKernels, "add_level_set_kernels");
  syntax.registerActionSyntax("AddLevelSetKernels", "Modules/LevelSet", "add_level_set_kernels");
  syntax.addDependency("add_level_set_kernels", "add_kernel");

  // level set kernel creation
  registerTask("add_level_set_postprocessors", false);
  registerAction(AddLevelSetPostprocessors, "add_level_set_postprocessors");
  syntax.registerActionSyntax("AddLevelSetPostprocessors", "Modules/LevelSet", "add_level_set_postprocessors");
  syntax.addDependency("add_level_set_postprocessors", "add_postprocessor");
}
