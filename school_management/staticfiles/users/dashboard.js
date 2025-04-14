document.addEventListener('DOMContentLoaded', () => {
    // Toggle sidebar
    const menuIcon = document.querySelector('.menu-icon');
    const sidebar = document.querySelector('.sidebar');
    
    menuIcon.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
        menuIcon.style.transform = sidebar.classList.contains('collapsed') 
            ? 'rotate(180deg)' 
            : 'rotate(0deg)';
    });

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', (e) => {
        const isMobile = window.innerWidth <= 768;
        const isClickOutsideSidebar = !sidebar.contains(e.target) && !menuIcon.contains(e.target);
        
        if (isMobile && isClickOutsideSidebar && !sidebar.classList.contains('collapsed')) {
            sidebar.classList.add('collapsed');
            menuIcon.style.transform = 'rotate(180deg)';
        }
    });

    // Enhanced hover effects for nav items
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
        item.addEventListener('mouseenter', (e) => {
            const icon = e.currentTarget.querySelector('.icon');
            icon.style.transform = 'scale(1.2) rotate(360deg)';
            
            // Add ripple effect
            const ripple = document.createElement('div');
            ripple.className = 'ripple';
            ripple.style.position = 'absolute';
            ripple.style.width = '20px';
            ripple.style.height = '20px';
            ripple.style.background = 'currentColor';
            ripple.style.opacity = '0.2';
            ripple.style.borderRadius = '50%';
            ripple.style.transform = 'scale(0)';
            ripple.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
            
            e.currentTarget.appendChild(ripple);
            
            // Trigger ripple animation
            requestAnimationFrame(() => {
                ripple.style.transform = 'scale(8)';
                ripple.style.opacity = '0';
                
                // Clean up
                setTimeout(() => {
                    ripple.remove();
                }, 600);
            });
        });

        item.addEventListener('mouseleave', (e) => {
            const icon = e.currentTarget.querySelector('.icon');
            icon.style.transform = 'scale(1) rotate(0)';
        });

        // Add click animation
        item.addEventListener('click', (e) => {
            const icon = e.currentTarget.querySelector('.icon');
            icon.style.transform = 'scale(0.9)';
            setTimeout(() => {
                icon.style.transform = 'scale(1)';
            }, 150);
        });
    });

    // Rotating quotes system
    const quotes = [
        "Education is the passport to the future, for tomorrow belongs to those who prepare for it today.",
        "The beautiful thing about learning is that no one can take it away from you.",
        "Education is not preparation for life; education is life itself.",
        "Knowledge is power. Information is liberating. Education is the premise of progress.",
        "The roots of education are bitter, but the fruit is sweet.",
        "Education is the most powerful weapon which you can use to change the world.",
        "Learning is not attained by chance, it must be sought for with ardor and diligence.",
        "The more that you read, the more things you will know. The more that you learn, the more places you'll go.",
        "Education is not the filling of a pail, but the lighting of a fire.",
        "Live as if you were to die tomorrow. Learn as if you were to live forever."
    ];

    function getRandomQuote() {
        return quotes[Math.floor(Math.random() * quotes.length)];
    }

    // Set initial quote
    const quoteElement = document.getElementById('quote');
    quoteElement.textContent = getRandomQuote();
    quoteElement.style.opacity = '4';

    // Add parallax effect to welcome section
    const welcomeSection = document.querySelector('.welcome-section');
    document.addEventListener('mousemove', (e) => {
        if (window.innerWidth > 768) {  // Only apply parallax on desktop
            const x = e.clientX / window.innerWidth;
            const y = e.clientY / window.innerHeight;
            
            welcomeSection.style.transform = `
                perspective(1000px)
                rotateX(${y * 2 - 1}deg)
                rotateY(${x * 2 - 1}deg)
                translateY(-5px)
            `;
        }
    });

    // Reset welcome section transform on mobile
    window.addEventListener('resize', () => {
        if (window.innerWidth <= 768) {
            welcomeSection.style.transform = 'none';
        }
    });
});