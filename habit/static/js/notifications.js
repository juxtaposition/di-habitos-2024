// Función utilitaria para obtener cookies (debe estar fuera y antes de todo)
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

document.addEventListener('DOMContentLoaded', function() {
    // Elementos DOM principales
    const notificationBell = document.querySelector('.notification-bell');
    const notificationMenu = document.querySelector('.notification-menu');

    // Funciones de UI
    function showEmptyState() {
        const emptyState = document.createElement('li');
        emptyState.className = 'notification-item no-notifications';
        emptyState.innerHTML = `
            <div class="empty-state">
                <i class="ph ph-check-circle"></i>
                <p>¡Todo al día!</p>
                <span>Te notificaremos cuando haya algo nuevo</span>
            </div>
        `;
        emptyState.style.animation = 'fadeIn 0.5s ease';
        notificationMenu.appendChild(emptyState);
    }

    function updateNotificationCount() {
        const unreadNotifications = document.querySelectorAll('.notification-item.unread').length;
        const badge = notificationBell.querySelector('.badge');

        if (unreadNotifications > 0) {
            notificationBell.classList.add('has-notifications');
            if (badge) {
                badge.textContent = unreadNotifications;
                badge.style.animation = 'scaleCount 0.3s ease';
            } else {
                const newBadge = document.createElement('span');
                newBadge.className = 'position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger notification-badge';
                newBadge.textContent = unreadNotifications;
                notificationBell.appendChild(newBadge);
            }
        } else {
            notificationBell.classList.remove('has-notifications');
            if (badge) {
                badge.style.animation = 'fadeOut 0.3s ease';
                setTimeout(() => badge.remove(), 300);
            }
        }
    }

    function handleNotificationRemoval(notificationElement) {
        notificationElement.style.animation = 'fadeOut 0.5s ease';
        setTimeout(() => {
            notificationElement.remove();
            updateNotificationCount();

            const remainingNotifications = document.querySelectorAll('.notification-item:not(.no-notifications)').length;
            if (remainingNotifications === 0) {
                showEmptyState();
            }
        }, 500);
    }

    function markNotificationAsRead(notificationId, notificationElement) {
        fetch(`/notifications/mark-as-read/${notificationId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                handleNotificationRemoval(notificationElement);
            }
        })
        .catch(error => console.error('Error:', error));
    }

    function updateNotificationsDropdown() {
        fetch('/notifications/get-latest/', {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.html) {
                notificationMenu.innerHTML = data.html;
                updateNotificationCount();
                setupNotificationListeners();
            }
        });
    }

    // Event Listeners
    function setupNotificationListeners() {
        const notificationItems = document.querySelectorAll('.notification-item:not(.no-notifications)');
        notificationItems.forEach(item => {
            item.addEventListener('click', function(e) {
                e.stopPropagation();
                const notificationId = this.getAttribute('data-notification-id');
                if (notificationId) {
                    markNotificationAsRead(notificationId, this);
                }
            });
        });
    }

    // Inicialización
    setupNotificationListeners();

    // Polling para nuevas notificaciones
    setInterval(function() {
        fetch('/notifications/check-new/')
            .then(response => response.json())
            .then(data => {
                if (data.new_notifications) {
                    updateNotificationsDropdown();
                }
            });
    }, 60000);

    // Debug logs
    console.log('Notification script loaded');
    console.log('Number of notification items:', document.querySelectorAll('.notification-item:not(.no-notifications)').length);
});