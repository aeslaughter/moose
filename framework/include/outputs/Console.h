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

#ifndef CONSOLE_H
#define CONSOLE_H

// MOOSE includes
#include "TableOutput.h"
#include "FormattedTable.h"
#include "Conversion.h"

// libMesh includes
#include "libmesh/string_to_enum.h"

// Forward declarations
class Console;

template<>
InputParameters validParams<Console>();

/**
 * An output object for writing to the console (screen)
 */
class Console :
  public TableOutput
{
public:

  /**
   * Class constructor
   */
  Console(const std::string & name, InputParameters);

  /**
   * Destructor
   */
  virtual ~Console();

  /**
   * Initial setup function
   * Prints the system information, this is done here so that the system information
   * is printed prior to any PETSc solve information
   */
  virtual void initialSetup();

  /**
   * Timestep function
   * Runs at the beginning of each timestep and prints the timestep, time, and dt information
   */
  virtual void timestepSetup();

  /**
   * Adds a outputting of nonlinear/linear residual printing to the base class output() method
   *
   * @see petscOutput
   */
  virtual void output();

  /**
   * Creates the output file name
   * Appends the user-supplied 'file_base' input parameter with a '.txt' extension
   * @return A string containing the output filename
   */
  virtual std::string filename();

  /**
   * Display the system information
   */
  void outputSystemInformation();

  /**
   * Add a message to the output streams
   * @param message The message to add to the output streams
   *
   * Any call to this method will write the supplied message to the screen and/or file,
   * following the same restrictions as outputStep and outputInitial
   *
   */
  void mooseConsole(const std::string & message, bool indent);

  /**
   * Output string for setting up PETSC output
   */
  static void petscSetupOutput();

protected:

  /**
   * Print the input file at the beginning of the simulation
   */
  virtual void outputInput();

  /**
   * Prints the aux scalar variables table to the screen
   */
  virtual void outputScalarVariables();

  /**
   * Prints the postprocessor table to the screen
   */
  virtual void outputPostprocessors();

  /**
   * Not implemented.
   */
  virtual void outputVectorPostprocessors() { mooseError("Can't currently output VectorPostprocessors to the screen"); };

  /**
   * A helper function for outputting norms in color
   * @param old_norm The old residual norm to compare against
   * @param norm The current residual norm
   */
  std::string outputNorm(Real old_norm, Real norm);

  /** Helper function function for stringstream formatting
   * @see outputSimulationInformation()
   */
  void insertNewline(std::stringstream &oss, std::streampos &begin, std::streampos &curr);

  /**
   * Write message to screen and/or file
   * @param message The desired message
   * @param indent True if multiapp indenting is desired
   */
  void write(std::string message, bool indent = true);

  /**
   * Apply indentation to newlines in the supplied stream
   * @param message Reference to the message being changed
   */
  void indentMessage(std::string & message);

/**
   * Write the file stream to the file
   * @param append Toggle for appending the file
   *
   * This helper function writes the _file_output_stream to the file and clears the
   * stream, by default the file is appended. This does nothing if 'output_file' is
   * false.
   */
  void writeStream(bool append = true);

  /**
   * Print the L2-norms for each variable
   */
  void writeVariableNorms();

  /// The max number of table rows
  unsigned int _max_rows;

  /// The FormattedTable fit mode
  MooseEnum _fit_mode;

  /// Toggle for controlling the use of color output
  bool _use_color;

  /// Toggle for outputting time in time and dt in scientific notation
  bool _scientific_time;

  /// Flag for controlling outputting console information to a file
  bool _write_file;

  /// Flag for controlling outputting console information to screen
  bool _write_screen;

  /// Flag for writing detailed time step information
  bool _verbose;

  /// Stream for storing information to be written to a file
  std::stringstream _file_output_stream;

  /// Storage for the old linear residual (needed for color output)
  Real _old_linear_norm;

  /// Storage for the old non linear residual (needed for color output)
  Real _old_nonlinear_norm;

  /// State for all performance logging
  bool _perf_log;

  /// State for solve performance log
  bool _solve_log;

  /// State for setup performance log
  bool _setup_log;

#ifdef LIBMESH_ENABLE_PERFORMANCE_LOGGING
  /// Control the display libMesh performance log
  bool _libmesh_log;
#endif

  /// State for early setup log printing
  bool _setup_log_early;

  /// State for the performance log header information
  bool _perf_header;

  /// Flag for writing all variable norms
  bool _all_variable_norms;

  /// Flag for writing outlier variable norms
  bool _outlier_variable_norms;

  /// Multipliers for coloring variable residual norms (default [2, 0.8])
  std::vector<Real> _outlier_multiplier;

  /// Number of significant digits
  unsigned int _precision;

  /// Width used for printing simulation information
  static const unsigned int _field_width = 25;

  /// Line length for printing simulation information
  static const unsigned int _line_length = 100;

private:

  /// State of the --timing command line argument from MooseApp
  bool _timing;

  /// Level of indent to add to output
  std::string _multiapp_indent;

  /// Reference to cached messages from calls to _console
  const std::ostringstream & _console_buffer;

  friend class OutputWarehouse;
};

#endif /* CONSOLE_H */
