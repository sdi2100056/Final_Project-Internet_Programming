

// Add form-control class to all form fields and remove placeholders
document.addEventListener('DOMContentLoaded', function() {
    const inputs = document.querySelectorAll('input[type="text"], input[type="email"], input[type="password"]');
    inputs.forEach(input => {
        input.classList.add('form-control');
        input.removeAttribute('placeholder');
    });
});