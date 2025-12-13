/**
 * Theme Toggle Functionality
 * Handles light/dark mode switching with localStorage persistence
 */

(function() {
    'use strict';

    // Get theme from localStorage or default to light
    const getStoredTheme = () => localStorage.getItem('theme') || 'light';
    const setStoredTheme = theme => localStorage.setItem('theme', theme);

    // Get theme from cookie (server-side preference)
    const getCookieTheme = () => {
        const name = 'theme=';
        const decodedCookie = decodeURIComponent(document.cookie);
        const ca = decodedCookie.split(';');
        for(let i = 0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) == ' ') {
                c = c.substring(1);
            }
            if (c.indexOf(name) == 0) {
                return c.substring(name.length, c.length);
            }
        }
        return null;
    };

    // Set theme on document
    const setTheme = theme => {
        document.documentElement.setAttribute('data-theme', theme);
        updateThemeIcon(theme);
        setStoredTheme(theme);
        
        // Update cookie for server-side persistence
        document.cookie = `theme=${theme}; path=/; max-age=31536000`; // 1 year
    };

    // Update theme toggle icon
    const updateThemeIcon = theme => {
        const themeIcon = document.getElementById('themeIcon');
        if (themeIcon) {
            if (theme === 'dark') {
                themeIcon.className = 'bi bi-sun-fill';
            } else {
                themeIcon.className = 'bi bi-moon-stars';
            }
        }
    };

    // Initialize theme on page load
    const initTheme = () => {
        // Priority: localStorage > cookie > default
        const storedTheme = getStoredTheme();
        const cookieTheme = getCookieTheme();
        const theme = storedTheme || cookieTheme || 'light';
        
        setTheme(theme);
    };

    // Toggle theme
    const toggleTheme = () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
        
        // Send theme preference to server
        fetch('/set-theme/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCsrfToken()
            },
            body: `theme=${newTheme}`
        }).catch(error => console.error('Error saving theme:', error));
    };

    // Get CSRF token from cookie
    const getCsrfToken = () => {
        const name = 'csrftoken=';
        const decodedCookie = decodeURIComponent(document.cookie);
        const ca = decodedCookie.split(';');
        for(let i = 0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) == ' ') {
                c = c.substring(1);
            }
            if (c.indexOf(name) == 0) {
                return c.substring(name.length, c.length);
            }
        }
        return '';
    };

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTheme);
    } else {
        initTheme();
    }

    // Add event listener to theme toggle button
    document.addEventListener('DOMContentLoaded', () => {
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', toggleTheme);
        }
    });

    // Add smooth scroll behavior
    document.addEventListener('DOMContentLoaded', () => {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                const href = this.getAttribute('href');
                if (href !== '#') {
                    e.preventDefault();
                    const target = document.querySelector(href);
                    if (target) {
                        target.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }
                }
            });
        });
    });

    // Auto-dismiss alerts after 5 seconds
    document.addEventListener('DOMContentLoaded', () => {
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(alert => {
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        });
    });

    // Form validation feedback
    document.addEventListener('DOMContentLoaded', () => {
        const forms = document.querySelectorAll('.needs-validation');
        forms.forEach(form => {
            form.addEventListener('submit', event => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            });
        });
    });

    // Handle currently working/studying checkboxes
    document.addEventListener('DOMContentLoaded', () => {
        const currentCheckboxes = document.querySelectorAll('[id$="_currently_working"], [id$="_currently_studying"]');
        currentCheckboxes.forEach(checkbox => {
            const endDateField = checkbox.closest('form').querySelector('[id$="_end_date"]');
            
            if (checkbox && endDateField) {
                const toggleEndDate = () => {
                    if (checkbox.checked) {
                        endDateField.disabled = true;
                        endDateField.required = false;
                        endDateField.value = '';
                    } else {
                        endDateField.disabled = false;
                        endDateField.required = true;
                    }
                };
                
                checkbox.addEventListener('change', toggleEndDate);
                toggleEndDate(); // Initialize on page load
            }
        });
    });

    // Confirm delete actions
    document.addEventListener('DOMContentLoaded', () => {
        const deleteButtons = document.querySelectorAll('[data-confirm-delete]');
        deleteButtons.forEach(button => {
            button.addEventListener('click', event => {
                if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                    event.preventDefault();
                }
            });
        });
    });

    // Add fade-in animation to cards
    document.addEventListener('DOMContentLoaded', () => {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        document.querySelectorAll('.card, .feature-card').forEach(card => {
            observer.observe(card);
        });
    });

})();
