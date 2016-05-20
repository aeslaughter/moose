# Diffusion

## Class Description
The Laplacian operator.


## Description

The steady-state diffusion equation on a domain $\Omega$ is defined as
$-\nabla \cdot \nabla u = 0 \in \Omega.$

The weak form of this equation, in inner-product notation, is given by:
$$(\nabla \phi_i, \nabla u_h) = 0 \quad \forall  \phi_i, $$
where $\phi_i$ are the test functions and $u_h$ is the finite element solution of $u$.


## Input Parameters
### General Parameters
| Name     | Type                    | Description                                           |
| -------- | ----------------------- | ----------------------------------------------------- |
| variable | `NonlinearVariableName` | The name of the variable that this Kernel operates on |

| Name         | Type                         | Description                                                                 |
| ------------ | ---------------------------- | --------------------------------------------------------------------------- |
| block        | `std::vector<SubdomainName>` | The list of block ids (SubdomainID) that this object will be applied        |
| control_tags | `std::vector<std::string>`   | Adds user-defined labels for accessing object parameters via control logic. |
| enable       | `bool`                       | Set the enabled status of the MooseObject.                                  |
| type         | `std::string`                |                                                                             |

### Advanced Parameters
| Name | Type | Description |
| ---- | ---- | ----------- |

| Name               | Type                           | Description                                                                                                                                                                                               |
| ------------------ | ------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| diag_save_in       | `std::vector<AuxVariableName>` | The name of auxiliary variables to save this Kernel's diagonal Jacobian contributions to. Everything about that variable must match everything about this variable (the type, what blocks it's on, etc.)  |
| implicit           | `bool`                         | Determines whether this object is calculated using an implicit or explicit form                                                                                                                           |
| save_in            | `std::vector<AuxVariableName>` | The name of auxiliary variables to save this Kernel's residual contributions to.  Everything about that variable must match everything about this variable (the type, what blocks it's on, etc.)          |
| seed               | `unsigned int`                 | The seed for the master random number generator                                                                                                                                                           |
| use_displaced_mesh | `bool`                         | Whether or not this object should use the displaced mesh for computation. Note that in the case this is true but no displacements are provided in the Mesh block the undisplaced mesh will still be used. |
