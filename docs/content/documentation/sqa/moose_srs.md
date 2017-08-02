!SQA-load system_requirements_specification.md

!SQA-template-item project_description
{{PROJECT}} is an open-source tool for solving partial differential equations using the finite element method.
!END-template-item

!SQA-template-item system_scope
{{PROJECT}} is a finite element simulation framework design for preforming fully-coupled nonlinear
solves.
!END-template-item

!SQA-template-item system_context
{{PROJECT}} is utilizes an object-oriented design to allow users to customize existing
code and build up a simulation in a modular fashion.
!END-template-item

!SQA-template-item system_requirements

!SQA-requirement-list Core Framework, I/O and Execution Control
    F1.10 The system shall allow support for user-defined object for controlling the execution stages of a simulation.
    F1.20 The system shall allow for user-defined time step selection for simulations using a time-based execution scheme.
    F1.30 The system shall allow for user-defined time step integration schemes for simulations using a time-based execution scheme.
    F1.40 The system shall support user-defined matrix preconditioning that may be applied during the solve stages.
    F1.50 The system should support a programmatic method for building up the necessary objects necessary for a simulation.
    F1.60 The system shall provide the ability to resume a previous simulation due to fault or intentional termination.
    F1.70 The system shall allow for user-defined output types for simulation data.
    F1.80 The system shall provide a method of providing improved initial guesses (also known as "predictions") for the solution at subsequent time steps.
    F1.90 The system shall support the creation of constraints relating otherwise independent degrees of freedom.

!END-template-item
