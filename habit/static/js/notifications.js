document.addEventListener('DOMContentLoaded', function() {
    const notificationBell = document.querySelector('.notification-bell');
    const notificationItems = document.querySelectorAll('.notification-item');

    // Actualizar el estado de las notificaciones
    function updateNotificationStatus(notificationId) {
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
                const notificationItem = document.querySelector(`[data-notification-id="${notificationId}"]`);
                notificationItem.classList.remove('unread');
                updateNotificationCount();
            }
        });
    }

    // Actualizar el contador de notificaciones
    function updateNotificationCount() {
        const unreadNotifications = document.querySelectorAll('.notification-item.unread').length;
        const badge = notificationBell.querySelector('.badge');

        if (unreadNotifications > 0) {
            notificationBell.classList.add('has-notifications');
            if (badge) {
                badge.textContent = unreadNotifications;
            } else {
                const newBadge = document.createElement('span');
                newBadge.className = 'position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger notification-badge';
                newBadge.textContent = unreadNotifications;
                notificationBell.appendChild(newBadge);
            }
        } else {
            notificationBell.classList.remove('has-notifications');
            if (badge) {
                badge.remove();
            }
        }
    }

    // Event listeners para las notificaciones
    notificationItems.forEach(item => {
        if (!item.classList.contains('no-notifications')) {
            item.addEventListener('click', function() {
                const notificationId = this.getAttribute('data-notification-id');
                updateNotificationStatus(notificationId);
            });
        }
    });

    // Verificar nuevas notificaciones cada minuto
    setInterval(function() {
        fetch('/notifications/check-new/')
            .then(response => response.json())
            .then(data => {
                if (data.new_notifications) {
                    location.reload();  // O actualizar el dropdown de manera más elegante
                }
            });
    }, 60000);
});