document.addEventListener('DOMContentLoaded', function () {

    Telegram.WebApp.ready();

    var initData = Telegram.WebApp.initData || '';
    var initDataUnsafe = Telegram.WebApp.initDataUnsafe || {};

    function getBoostLvl() {
        if (!initDataUnsafe.query_id) {
            alert('WebViewQueryId not defined');
            return;
        }
        $.ajax('/getBoostLvl', {
            type: 'POST',
            data: {
                _auth: initData,
            },
            dataType: 'json',
            success: function (result) {
                if (result.ok) {
                    var clicksBoost = document.getElementById('clicks_lvl')
                    var clicks5min = document.getElementById('5min_lvl')
                    var clicksBoostCost = document.getElementById('clicks_cost')
                    var clicks5minCost = document.getElementById('5min_cost')
                    clicksBoostCost.textContent = `${result.OneClickMoneyCost} coins`
                    clicks5minCost.textContent = `${result.ClicksPerhaps5minCost} coins`
                    clicksBoost.textContent = `Уровень: ${result.OneClickMoney}`
                    clicks5min.textContent = `Уровень: ${result.ClicksPerhaps5min}`
                } else {
                    alert('Unknown error');
                }
            },
            error: function (xhr) {
                alert('Server error');
            }
        });
    }

    function buyBoost(boostId) {
        if (!initDataUnsafe.query_id) {
            alert('WebViewQueryId not defined');
            return;
        }
        $.ajax('/buyBoost', {
            type: 'POST',
            data: {
                _auth: initData,
                boostId: boostId,
            },
            dataType: 'json',
            success: function (result) {
                if (result.ok) {
                    if (result.OneClickMoney && result.ClicksPerhaps5min && result.OneClickMoneyCost && result.ClicksPerhaps5minCost) {
                        var clicksBoost = document.getElementById('clicks_lvl')
                        var clicks5min = document.getElementById('5min_lvl')
                        var clicksBoostCost = document.getElementById('clicks_cost')
                        var clicks5minCost = document.getElementById('5min_cost')
                        clicksBoostCost.textContent = `${result.OneClickMoneyCost} coins`
                        clicks5minCost.textContent = `${result.ClicksPerhaps5minCost} coins`
                        clicksBoost.textContent = `Уровень: ${result.OneClickMoney}`
                        clicks5min.textContent = `Уровень: ${result.ClicksPerhaps5min}`

                        alert('Успешно!')
                    } else {
                        alert(result.error)
                    }

                } else {
                    alert('Unknown error');
                }
            },
            error: function (xhr) {
                alert('Server error');
            }
        });
    }

    getBoostLvl()

    const closeModal = document.getElementById('close');
    const modal = document.getElementById('modal');
    const boosts = document.querySelectorAll('.boost');
    const buyModal = document.getElementById('buy')

    // Обработчик события для каждого буста
    boosts.forEach(function (boost) {
        boost.addEventListener('click', function () {
            const boostId = boost.id; // Получаем id буста
            if (boostId) {
                modal.style.display = 'block'; // Показываем модальное окно
                localStorage.setItem('selectedBoost', boostId); // Сохраняем id буста в локальное хранилище
            }
        });
    });

    closeModal.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    buyModal.addEventListener('click', () => {
        modal.style.display = 'none'

        const selectedBoost = localStorage.getItem('selectedBoost');

        buyBoost(selectedBoost)

    })
});
