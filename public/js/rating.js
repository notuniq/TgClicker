document.addEventListener('DOMContentLoaded', function() {

    function formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
    }

    var ratingBodyElement = document.querySelector('.rating_body'); // Находим элемент с классом rating_body

    Telegram.WebApp.ready();

    var initData = Telegram.WebApp.initData || '';
    var initDataUnsafe = Telegram.WebApp.initDataUnsafe || {};

    function getTopUsers() {
        if (!initDataUnsafe.query_id) {
            alert('WebViewQueryId not defined');
            return;
        }
        $.ajax('/topUsers', {
            type: 'POST',
            data: {
                _auth: initData
            },
            dataType: 'json',
            success: function (result) {
                if (result.ok) {
                    // Очищаем предыдущие данные
                    ratingBodyElement.innerHTML = '';
                    // Добавляем данные о топ 5 пользователях
                    var myTopId = document.getElementById('myTop')

                    myTopId.textContent = `У вас ${result.user_position} место!`

                    result.top_users.forEach(function (user) {
                        var userRatingElement = document.createElement('div');
                        userRatingElement.classList.add('user_rating');

                        // Создаем элемент img с классом avatar
                        var avatarElement = document.createElement('img');
                        avatarElement.classList.add('avatar');
                        avatarElement.src = `https://dbf6-77-105-140-135.ngrok-free.app/avatars/${user.photo_url}`;
                        avatarElement.alt = 'Avatar';

                        // Создаем элемент span с классом username
                        var usernameElement = document.createElement('span');
                        usernameElement.classList.add('username');
                        usernameElement.textContent = user.first_name;

                        var levelElement = document.createElement('span')
                        levelElement.classList.add('level')
                        levelElement.textContent = `${formatNumber(user.balance)} $`
                        // Добавляем созданные элементы в элемент div с классом user_rating
                        userRatingElement.appendChild(avatarElement);
                        userRatingElement.appendChild(usernameElement);
                        userRatingElement.appendChild(levelElement)

                        // Добавляем элемент div с классом user_rating в элемент с классом rating_body
                        ratingBodyElement.appendChild(userRatingElement);
                    });
                } else {
                    alert('Unknown error');
                }
            },
            error: function (xhr) {
                alert('Server error');
            }
        });
    }

    // Вызываем функцию getTopUsers() после полной загрузки страницы
    getTopUsers();
});
