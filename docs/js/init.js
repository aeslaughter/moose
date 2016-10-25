// Setup MathJax
MathJax.Hub.Config({
    tex2jax: {
        skipTags: ['script', 'noscript', 'style', 'textarea', 'pre'],
        inlineMath: [['$','$'], ['\\(','\\)']]
    }
});

// Materialize side navigation
$(".button-collapse").sideNav();

// Materialize scrolling table-of-contents
$(document).ready(function(){
    $('.scrollspy').scrollSpy();
});


//$("h1","h2").addClass("section scollSpy");
