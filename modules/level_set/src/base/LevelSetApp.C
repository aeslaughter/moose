#include "Moose.h"
#include "LevelSetApp.h"
#include "AppFactory.h"
#include "MooseSyntax.h"

// Kernels
#include "LevelSetAdvection.h"
#include "LevelSetAdvectionSUPG.h"
#include "LevelSetTimeDerivativeSUPG.h"
#include "LevelSetOlssonReinitialization.h"

// Functions
#include "LevelSetGaussianHill.h"
#include "LevelSetBubbleFunction.h"
#include "LevelSetVortex.h"

// Postprocessors
#include "LevelSetCFLCondition.h"
#include "LevelSetVolume.h"
#include "LevelSetOlssonTerminator.h"

// Markers
#include "LevelSetValueMarker.h"

// Problems
#include "LevelSetProblem.h"
#include "LevelSetReinitializationProblem.h"

// MultiApps
#include "LevelSetReinitializationMultiApp.h"

// Transfers
#include "LevelSetMeshRefinementTransfer.h"

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
}

void
LevelSetApp::registerObjects(Factory & factory)
{
  // Kernels
  registerKernel(LevelSetAdvection);
  registerKernel(LevelSetAdvectionSUPG);
  registerKernel(LevelSetTimeDerivativeSUPG);
  registerKernel(LevelSetOlssonReinitialization);

  // Functions
  registerFunction(LevelSetGaussianHill);
  registerFunction(LevelSetBubbleFunction);
  registerFunction(LevelSetVortex);

  // Postprocessors
  registerPostprocessor(LevelSetCFLCondition);
  registerPostprocessor(LevelSetVolume);
  registerPostprocessor(LevelSetOlssonTerminator);

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
LevelSetApp::associateSyntax(Syntax & /*syntax*/, ActionFactory & /*action_factory*/)
{
}
