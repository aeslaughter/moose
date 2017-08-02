{% import 'macros.md' as macros %}

# {{PROJECT}} System Requirement Specification
{% call macros.define("project_description") %}
Include a brief description of the project.
{% endcall %}

## Introduction
### System Purpose
{% call macros.define("system_purpose", default=True) %}
The purpose of this document is to specify the software requirements necessary to achieve the function and capabilities presented in the {{PROJECT}} Theory Manual. This specification is intended for use by those performing nuclear power plant (NPP) reactor systems safety analysis.
{% endcall %}

### System Scope
{% call macros.define("system_scope") %}
Delineate the following:

1. Identify the product(s) to be produced by name (Network Infrastructure, Host DBMS, Report Generator, HPC Server, etc.)
1. Explain what the product(s) will, and, if necessary, will not do
1. Describe the application of the product being specified, including relevant benefits, objectives, and goals.
{% endcall %}

### System Overview
#### System Context
{% call macros.define("system_context") %}
Describe at a general level the major elements of the system including user roles and how they interact. The system overview includes appropriate diagrams and narrative to provide the context of the system, defining all significant interfaces crossing the system's boundaries.
{% endcall %}

## System Requirements
{% call macros.define("system_requirements") %}
List the requirement for the system, using the following syntax.
```
!SQA-requirement-list Group Name
    R1.0 The system shall solve an equation.
    R1.1 The system shall solve another equation.
```
{% endcall %}
