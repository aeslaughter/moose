!devel /Kernels/LevelSetAdvection float=right width=auto margin=20px padding=20px background-color=#F8F8F8

# LevelSetAdvection
!description /Kernels/LevelSetAdvection

The level set equation is typically defined as below. As shown in this equation, the `LevelSetAdvection` kernel
implements the advection portion of the equation.

$$
\frac{\partial u}{\partial t} + \underbrace{\vec{v} \cdot \nabla u}_{\textrm{LevelSetAdvection}} = 0,
$$
where $u$ is the level set variable, $t$ is time, and $\vec{v}$ is a known velocity field that
advects the level set variable.

!parameters /Kernels/LevelSetAdvection

!inputfiles /Kernels/LevelSetAdvection

!childobjects /Kernels/LevelSetAdvection
