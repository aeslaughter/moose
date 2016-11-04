# Level Set Module
## Introduction
The level set method is commonly used for front tracking problems \cite{osher2006level}. It
is modeled with the multi-dimensional advection equation

\begin{equation}
\frac{\partial u}{\partial t} + \vec{v}\cdot\nabla u = 0,
\label{eqn:pure_advection}
\end{equation}

where $t$ is time, $\vec{v}$ is a known velocity field, and $u$ is the
variable representing the interface. Traditionally $u$ is taken to be
the signed distance from the interface.  This problem poses
significant challenges: numerical stabilization techniques must be
employed to avoid node-to-node oscillations, and intermediate
re-initialization steps must be undertaken to evolve the interface in
a physically-consistent manner.

The basic requirements for solving the level set equation in MOOSE are
summarized in the following milestone objectives:

* Solve the level set equation numerically using the Galerkin finite element method.
* Apply a standard stabilization scheme.
* Implement a basic re-initialization scheme.
In order to test and demonstrate the use of the level set module, a benchmark
rotating bubble problem requiring each of the three aforementioned
components was undertaken.

## Weak Form
The weak form of \eqref{eqn:pure_advection} is: find $u_h \approx u$ such that

\begin{equation}
\left(\frac{\partial u_h}{\partial t}, \psi_i\right) + (\vec{v} \cdot \nabla u_h, \psi_i) = 0
\label{eqn:pure_advection_weak}
\end{equation}

holds for all admissible test functions, $\psi_i$.  Here $u_h$ is the
finite element approximation to $u$, and we have employed the
inner-product notation $(u,v) \equiv \int_{\Omega} uv \;\text{d}x$ for
convenience.  Solving \eqref{eqn:pure_advection_weak} in MOOSE
requires the addition of a single physics kernel for the second term
on the left-hand side of \eqref{eqn:pure_advection_weak}. This kernel
is included in the level set module as [LevelSetAdvection](LevelSetAdvection.md), and
allows one to use coupled variables to represent the velocity field.

## Stabilization
As with any pure convection equation, implementing the level set
equation with the Galerkin finite element method requires numerical
stabilization if node-to-node oscillations are to be avoided and
standard solution accuracy is to be maintained.  The level set module also
includes kernels which implement the Streamline Upwind/Petrov-Galerkin
(SUPG) stabilization method \cite{brooks1982streamline,donea2003finite}
for \eqref{eqn:pure_advection_weak}, which is given by

\begin{equation}
\label{eqn:supg}
\left(\frac{\partial u_h}{\partial t} + \vec{v}\cdot\nabla u_h, \psi_i + \frac{h}{2\|\vec{v}\|}(\vec{v} \cdot \nabla\psi_i)\right) = 0,
\end{equation}
where $h$ is the element length, and $\|\vec{v}\|$ is the Euclidean
norm of the velocity vector.  We note that the $h$-dependent terms add
stability to the numerical scheme by introducing the
symmetric, velocity-dependent artificial viscosity contribution:

\begin{align}
  \left(\frac{h}{2\|\vec{v}\|} \vec{v}\cdot\nabla u_h, \vec{v} \cdot \nabla\psi_i \right)
\end{align}
in a so-called "consistent" manner.  That is, if the true solution
$u$ satisfies \eqref{eqn:pure_advection}, it is easy to see, by
inspection, that it will also satisfy \eqref{eqn:supg}, since the
strong form of the residual appears in the first "slot" of the
inner product.  The stabilization terms are implemented in the code as
two additional kernels: [LevelSetTimeDerivativeSUPG](LevelSetTimeDerivativeSUPG.md) and
[LevelSetAdvectionSUPG](LevelSetAdvectionSUPG.md).

## Re-initialization
The advected variable $u$ is often used to track a moving front, and
therefore it is desirable that the total amount of $u$ present in
$\Omega$ remain the same throughout the simulation.  This is
equivalent to stating that the area within a given contour of $u$
does not change. It is also frequently desirable that $u$ remain a
signed distance function throughout the course of the simulation.
There is a vast amount of research into methods which guarantee either
conservation, the signed distance property, or both.  The level set
module in MOOSE currently implements a conservative
"re-initialization" algorithm that transforms $u_h$ into a smooth
function in the range $[0, 1]$ rather than a signed distance, which is
useful for certain types of problems such as phase identification.

The weak form of the re-initialization equation is: find $U_h$ such that

\begin{equation}
  \label{eqn:reinit_weak}
  \left(\frac{\partial U_h}{\partial \tau}, \psi_i\right) + \left(\nabla\psi_i, (-f + \epsilon\nabla U_h\cdot\hat{n}_{\ast})\hat{n}_{\ast}\right) = 0,
\end{equation}
holds for every admissible $\psi_i$, where $\tau$ is the pseudo time
during the re-initialization, $\hat{n}_{\ast}$ is the normal vector
computed from the level set variable $u_h$ at pseudo time $\tau=0$,
$\epsilon$ is the interface thickness, $f\equiv U_h(1-U_h)$, and
$U_h(\tau=0) = u_h$. Steady-state for $U_h$ is detected when

\begin{equation}
  \label{eqn:steady_state}
  \frac{\|U_h^{m+1} - U_h^{m}\|}{\Delta\tau} < \delta,
\end{equation}
where $\delta$ is a problem-dependent tolerance, and $U_h^m \equiv
U_h(\tau=m\Delta \tau)$.  When steady-state is achieved, $u_h$ is set
equal to the re-initialized solution $U_h$, and the entire process
is repeated at time $t+\Delta t$.

The majority of the MOOSE level set module implementation effort was
focused on the addition of this re-initialization algorithm.
Improvements to the MOOSE `MultiApp` system, such as a more robust
solution copy function and an improved full-solve `MultiApp`,
allowed the level set equation and the re-initialization problem to be
solved on the same variable at each time step.

## Example Results
A typical benchmark problem for the level set equation is the rotating
bubble. The problem involves initializing $u_h$ with a "bubble" of
radius 0.15 at $(0.0, 0.5)$ for $\Omega = [-1,1]^2$.  This bubble is
then advected with the given velocity field $\vec{v}=(4y,-4x)$, so that, at
$t=\pi/2$, the bubble should return to its original position.

The figure below shows the results of running this problem using the level set
equation alone, the SUPG stabilized level set equation, and the
re-initialized level set equation. Initial condition (black contour) and final state (green contour)
after two revolutions at time $t=\pi$ for the basic level set equation (left),
SUPG method (middle), and re-initialization method (right).


!image media/level_set/level_set_only.png caption=Level set equation only. width=33% float=left id=fig:level_set_only

!image media/level_set/level_set_with_supg.png caption=Level set with SUPG. width=33% float=left id=fig:level_set_with_supg

!image media/level_set/level_set_with_reinit.png caption=Level set with re-initialization. width=33% float=left id=fig:level_set_with_reinit


Figure~\ref{fig:area_comparison} is a plot of the area of
the circle during the three simulations. Note that in the
unstabilized, un-reinitialized level set equation, both area
conservation and stability issues are readily apparent. The
instabilities are especially obvious in Figure~\ref{fig:area_comparison}, where the drastic
area changes are due to numerical oscillations in the solution
field. Adding SUPG stabilization helps ameliorate the stability
concern but it suffers from loss of area conservation. The
re-initialization scheme is both stable and area-conserving.

!image

## References
\bibliographystyle{unsrt}
\bibliography{bib/level_set.bib}
