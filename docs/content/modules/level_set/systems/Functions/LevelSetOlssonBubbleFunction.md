# LevelSetOlssonBubbleFunction
!devel /Functions/LevelSetOlssonBubbleFunction float=right width=auto margin=20px padding=20px background-color=#F8F8F8

!description /Functions/LevelSetOlssonBubbleFunction

\citet{olsson2005conservative} define a level set function ($\Phi$) that differs from the traditional signed distance function.
They define a level set function ranging from 0 to 1 with a defined thickness ($\epsilon$), which
is a commonly referred to as a smeared Heaviside function ($H_{sm}(\Phi)$):

$$
\begin{equation}
H_{sm}(\Phi) = \begin{cases}
0, & \Phi < -\epsilon, \\
\frac{1}{2} + \frac{\Phi}{2\epsilon} + \frac{1}{2\pi}\sin(\frac{\pi\Phi}{\epsilon}), & -\epsilon \le \Phi \le \epsilon,\\
1, & \Phi > \epsilon.
\end{cases}
\end{equation}
$$


!image media/level_set_olsson_bubble.png float=right width=30%

Typically, the interface of the level set function is defined by the 0.5 contour. For example, the following code creates a "bubble" in the
lower left corner in a domain ranging from 0 to 1 in the x- and y-direction.

!input modules/level_set/tests/functions/olsson_bubble_function/olsson_bubble_function.i block=Functions

!parameters /Functions/LevelSetOlssonBubbleFunction

!inputfiles /Functions/LevelSetOlssonBubbleFunction

!childobjects /Functions/LevelSetOlssonBubbleFunction

## References
\bibliographystyle{unsrt}
\bibliography{docs/bib/level_set.bib}
