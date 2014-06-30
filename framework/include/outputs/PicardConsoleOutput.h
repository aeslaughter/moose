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

#ifndef PICARDCONSOLEOUTPUT_H
#define PICARDCONSOLEOUTPUT_H

// MOOSE includes
#include "TableOutput.h"

// Forward declerations
class PicardConsoleOutput;

template<>
InputParameters validParams<PicardConsoleOutput>();

/**
 *
 */
class PicardConsoleOutput : public TableOutput
{
public:

  /**
   * Class constructor
   * @param name
   * @param InputParameters
   */
  PicardConsoleOutput(const std::string & name, InputParameters parameters);

  /**
   * Class destructor
   */
  virtual ~PicardConsoleOutput();

protected:
  virtual void outputPostprocessors();

  std::string filename()
    {
      return std::string();
    }


};

#endif //PICARDCONSOLEOUTPUT_H
