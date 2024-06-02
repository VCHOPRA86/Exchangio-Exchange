(function($) {
    "use strict";
    
    // Sticky Navbar
    // Checks the scroll position of the window
    $(window).scroll(function() {
        // Current vertical position of the scroll bar
        var scroll = $(window).scrollTop();
     // If the scroll position is greater than or equal to 50
        if (scroll >= 50) {
            // Add the class 'nav-sticky' to elements with the class 'sticky'
            $(".sticky").addClass("nav-sticky");
        } else {
             // Otherwise, remove the class 'nav-sticky'
            $(".sticky").removeClass("nav-sticky");
        }
        
    });

    // Smooth Link
    // function enables smooth scrolling for links
    $('.nav-item a, .mouse-down a').on('click', function(event) {
        // Store the clicked link
        var $anchor = $(this);
        // Animate the scrolling to the section the link points to
        $('html, body').stop().animate({
            // Scroll to the vertical position of the target section
            // minus an offset (here, it's set to 0)
            scrollTop: $($anchor.attr('href')).offset().top - 0
        }, 1500, 'easeInOutExpo'); // Duration of the animation (1500ms) and easing function
        // Prevent the default action of the click event
        event.preventDefault();
    });
})(jQuery);


