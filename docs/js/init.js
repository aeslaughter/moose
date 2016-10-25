// Setup MathJax
MathJax.Hub.Config({
    tex2jax: {
        skipTags: ['script', 'noscript', 'style', 'textarea', 'pre'],
        inlineMath: [['$','$'], ['\\(','\\)']]
    }
});

// Materialize side navigation
(function($){
  $(function(){
    $('.button-collapse').sideNav();

      // Show sideNav
      $('.button-collapse').sideNav('show');
      // Hide sideNav
      $('.button-collapse').sideNav('hide');

  }); // end of document ready
})(jQuery); // end of jQuery name space

// Materialize scrolling table-of-contents
//$(document).ready(function(){
//    $('.scrollspy').scrollSpy();
//});


//$("h1","h2").addClass("section scollSpy");
vb
