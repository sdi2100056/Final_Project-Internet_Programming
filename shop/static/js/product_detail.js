// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Helper function to show notifications
function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} position-fixed top-0 start-50 translate-middle-x mt-3`;
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'} me-2"></i>
        <strong>${message}</strong>
    `;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.transition = 'opacity 0.3s';
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Star Rating Click Handler
document.addEventListener('DOMContentLoaded', function() {
    const stars = document.querySelectorAll('.star-input');
    const ratingValue = document.getElementById('rating-value');

    if (ratingValue && stars.length > 0) {
        if (ratingValue.value > 0) {
            updateStars(parseInt(ratingValue.value));
        }

        stars.forEach((star, index) => {
            star.addEventListener('click', function() {
                const rating = parseInt(this.getAttribute('data-rating'));
                ratingValue.value = rating;
                updateStars(rating);
            });

            star.addEventListener('mouseenter', function() {
                const rating = parseInt(this.getAttribute('data-rating'));
                updateStars(rating);
            });
        });

        document.getElementById('star-rating').addEventListener('mouseleave', function() {
            const currentRating = parseInt(ratingValue.value) || 0;
            updateStars(currentRating);
        });
    }

    function updateStars(rating) {
        stars.forEach((star, index) => {
            if (index < rating) {
                star.classList.remove('far');
                star.classList.add('fas', 'active');
            } else {
                star.classList.remove('fas', 'active');
                star.classList.add('far');
            }
        });
    }
});

// Submit Rating via AJAX
function submitRating(productId) {
    const rating = document.getElementById('rating-value').value;
    const review = document.getElementById('review-text').value;

    if (rating === '0') {
        showNotification('Please select a rating!', 'warning');
        return;
    }

    $.ajax({
        url: `/rating/add/${productId}/`,
        type: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        data: {
            rating: rating,
            review: review
        },
        success: function(data) {
            if (data.success) {
                showNotification(data.message, 'success');
                setTimeout(() => location.reload(), 1500);
            } else {
                showNotification('Error: ' + (data.message || 'Something went wrong'), 'danger');
            }
        },
        error: function(xhr) {
            if (xhr.status === 403 || xhr.status === 401) {
                showNotification('Please login to rate this product', 'warning');
                setTimeout(() => {
                    window.location.href = '/login/?next=' + window.location.pathname;
                }, 1500);
            } else {
                showNotification('Network error. Please try again.', 'danger');
            }
        }
    });
}

// Add to Cart via AJAX
function addToCart(productId) {
    $.ajax({
        url: `/cart/add/${productId}/`,
        type: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        success: function(data) {
            if (data.success) {
                showNotification(data.message, 'success');
                const cartCount = document.getElementById('cart-count');
                if (cartCount) {
                    cartCount.textContent = data.cart_count;
                }
            } else {
                showNotification(data.message || 'Error adding product to cart', 'danger');
            }
        },
        error: function(xhr) {
            console.error('Error details:', xhr);
            showNotification('Error adding product to cart. Please try again.', 'danger');
        }
    });
}