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

function removeFromCart(itemId) {
    if (confirm('Remove the product?')) {
        $.ajax({
            url: `/cart/remove/${itemId}/`,
            type: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            success: function(data) {
                if (data.success) {
                    // Remove the item card from DOM
                    $(`#item-${itemId}`).fadeOut(300, function() {
                        $(this).remove();

                        // Update cart count and total
                        $('#cart-count').text(data.cart_count);
                        $('#cart-total').text(data.cart_total.toFixed(2));

                        // If cart is empty, reload page to show empty message
                        if (data.cart_count === 0) {
                            location.reload();
                        }
                    });
                } else {
                    alert('Error removing product');
                }
            },
            error: function() {
                alert('Error removing product. Please try again.');
            }
        });
    }
}