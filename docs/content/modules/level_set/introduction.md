# Level Set Module
The level set equation is typically defined as
$$
\frac{\partial \phi}{\partial t} + \vec{v} \cdot \nabla \phi = 0,
$$
where $phi$ is the level set variable, $t$ is time, and $\vec{v}$ is a known advective velocity field.

For incompressible flows ($\nabla \cdot \vec{v} = 0$) this equation can be written as
$$
\frac{\partial \phi}{\partial t} + \nabla \cdot (\phi\vec{v}) = 0.
$$
