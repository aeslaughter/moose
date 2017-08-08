{% import 'macros.md' as macros %}

# {{PROJECT}} System Requirement Specification
## Introduction
### System Purpose
{% call macros.define("system_purpose", default=True) %}
Summarize the reason(s) for the system being developed or modified.
{% endcall %}

### System Scope
{% call macros.define("system_scope") %}
Delineate the following:

1.	Identify the product(s) to be produced by name (Network Infrastructure, Host DBMS, Report Generator, HPC Server, etc.)
2.	Explain what the product(s) will, and, if necessary, will not do
3.	Describe the application of the product being specified, including relevant benefits, objectives, and goals.

!admonition note Be consistent with similar statements in higher level specifications (e.g.,
business requirements specification). {% endcall %}

### System Overview
#### System Context
{% call macros.define("system_context") %}
Describe at a general level the major elements of the system including user roles and how they
interact. The system overview includes appropriate diagrams and narrative to provide the context of
the system, defining all significant interfaces crossing the system’s boundaries.
{% endcall %}

#### System Functions
{% call macros.define("system_functions") %}
Provide a summary of the major use cases or functions, conditions, and constraints. For example, a specification for an accounting program may use this part to address customer account maintenance, customer statement, and invoice preparation without mentioning the vast amount of detail that each of those functions requires.

Sometimes the function summary that is necessary for this part can be taken directly from the section of the higher-level specification (if one exists) that allocates particular functions to the product. Note that for the sake of clarity:

1. The functions should be organized in a way that makes the list of functions understandable to the
customer or to anyone else reading the document for the first time.
2. Textual or graphical methods can be used to show the different functions and their relationships. Such a diagram is not intended to show a design of a product, but simply shows the logical relationships among variables.

Example:
Use Case: Submit Timesheet
Diagram: (insert diagram here)

Brief Description: The Employee enters hourly data for the week and submits for approval.
Initial Step-By-Step Description:

Before entering their timesheet, the employee must select the “ETS” or “ETS with Login Prompt” menu option from Nucleus and be logged into the Human Resource application.

1. The system presents the timesheet data entry interface to the employee with any previously saved data.
2. The employee enters charge No., TRC, and hours for each work day.
3. The employee may click “Save for Later,” exit, and return at a later time to complete timesheet OR the employee may click “Submit” to submit timesheet.
4. Following submittal, the system verifies the information (e.g., 40 hours). If information is not correct or complete, the employee will receive a warning; otherwise, the employee will be provided a confirmation that the time sheet was submitted with date and time.
{% endcall %}

#### User Characteristics
{% call macros.define("user_characteristics") %}
Identify each type of user/operator/maintainer of the system (by function, location, type of device), the number in each group, and the nature of their use of the system.
{% endcall %}

#### Assumptions and Dependencies
{% call macros.define("assumptions_and_dependencies") %}
List each of the factors that affect the requirements and should be taken into consideration for derivation of lower level requirements and design. These factors should include design inputs, design constraints, and installation considerations. Changes to these can affect the requirements in the specification. For example, an assumption may be that a specific operating system will be available on the hardware designated for the product. If, in fact, the operating system is not available, the specification would then have to change accordingly.
{% endcall %}

## Reference
{% call macros.define("user_characteristics") %}
ASME NQA 1 2008 with the NQA-1a-2009 addenda, “Quality Assurance Requirements for Nuclear Facility Applications,” First Edition, August 31, 2009.

ISO/IEC/IEEE 24765:2010(E), “Systems and software engineering — Vocabulary,” First Edition, December 15, 2010.

LWP 13620, “Managing Information Technology Assets,” Rev. 16, December 23, 2013.]
{% endcall %}

## Definitions and Acronyms
### Definitions
{% call macros.define("definitions") %}
*Baseline:* A specification or product (e.g., project plan, maintenance and operations [M&O] plan,
*requirements, or design) that has been formally reviewed and agreed upon, that thereafter serves as
*the basis for use and further development, and that can be changed only by using an approved change
*control process. [ASME NQA-1-2008 with the NQA-1a-2009 addenda edited]

*Validation:* Confirmation, through the provision of objective evidence (e.g., acceptance test),
*that the requirements for a specific intended use or application have been fulfilled. [ISO/IEC/IEEE
*24765:2010(E) edited]

*Verification:* (1) The process of: evaluating a system or component to determine whether the
*products of a given development phase satisfy the conditions imposed at the start of that phase.
*(2) Formal proof of program correctness (e.g., requirements, design, implementation reviews, system
*tests). [ISO/IEC/IEEE 24765:2010(E) edited]]
{% endcall %}

### Acronyms
{% call macros.define("definitions") %}
ASME American Society of Mechanical Engineers
DOE Department of Energy
IEC International Electrotechnical Commission
IEEE Institute of Electrical and Electronics Engineers
INL Idaho National Laboratory
ISO International Organization for Standardization
IT Information Technology
M&O Maintenance and Operations
NQA Nuclear Quality Assurance
QA Quality Assurance
V&V Verification and Validation
{% endcall %}

## System Requirements
{% call macros.define("minimum_requirements") %}

For software projects, the following is required:

1. The software requirements shall include technical requirements including operating system,
function, interfaces, performance, and security requirements, installation considerations, design
inputs, and any design constraints.
2. Identify applicable reference drawings, specifications, codes, standards, regulations,
procedures, or instructions that establish software requirement test, inspection, and acceptance
criteria.
3. Software requirements shall be traceable throughout the life cycle.
4. Security requirements shall be specified commensurate with the risk from unauthorized access or
use.

{% endcall %}

### Functional Requirements
{% call macros.define("functional_requirements") %}
This section of the specification should contain all of the use cases or functional requirements to
a level of detail sufficient to enable designers to design a system to satisfy those requirements,
and testers to test that the system satisfies those requirements.

1. Functional requirements must be stated in form to be:
    * Correct
    * Unambiguous
    * Complete
    * Consistent
    * Verifiable
    * Traceable.
2. Functional requirements should be cross-referenced to earlier documents that relate (e.g., business requirements).
3. Functional requirements should be uniquely identifiable.
4. Careful attention should be given to organizing the requirements to maximize readability.
List each function and its defining requirements here. For each function that is defined, one or more requirements are then described that define the functionality. The requirements should be as objective and measurable as possible.

Use one of the following examples as a guide for formatting the requirements.

!admonition note
These examples are for reference only and are not complete for the specified function.

*Example 1: IEEE Structured Requirements*

```
!SQA-requirement-list Group Name
    R1.0 The system shall solve an equation.
    R1.1 The system shall solve another equation.
```

{% endcall %}

### Usability Requirements

### Performance Requirements

### System Interface

## System Operations
### Human Systems Integration Requirements

### Maintainability

### Reliability

### System Modes and States

### Physical Characteristics

### Environmental Conditions

### System Security

### Information Management

### Policies and Regulations (not required for QL-2)

### System Live Cycle Sustainment

### Packaging, Handling, Shipping, and Transportation

## Verification

## Appendixes
