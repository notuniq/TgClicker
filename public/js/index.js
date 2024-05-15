document.addEventListener('DOMContentLoaded', function() {
    var clickCount = 0;
    var clickLimit = 500;
    var clickInterval = 5 * 60 * 1000; // 5 минут в миллисекундах
    var lastClickTime = 0;

    function formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
    }

    Telegram.WebApp.ready();

    var initData = Telegram.WebApp.initData || '';
    var initDataUnsafe = Telegram.WebApp.initDataUnsafe || {};

    function getBoostClicks() {
        return new Promise(function(resolve, reject) {
            if (!initDataUnsafe.query_id) {
                alert('WebViewQueryId not defined');
                reject('WebViewQueryId not defined');
                return;
            }

            $.ajax('/getBoostLvl', {
                type: 'POST',
                data: {
                    _auth: initData,
                },
                dataType: 'json',
                success: function(result) {
                    if (result.ok) {
                        resolve({
                            clickCost: result.ClicksMoney,
                            clicks5min: result.Clicks5min,
                            myClicks: result.UserClicks,
                        });

                    } else {
                        alert('Unknown error');
                        reject('Unknown error');
                    }
                },
                error: function(xhr) {
                    alert('Server error');
                    reject('Server error');
                }
            });
        });
    }

    function getCoins() {
        if (!initDataUnsafe.query_id) {
            alert('WebViewQueryId not defined');
            return;
        }
        $.ajax('/getCoins', {
            type: 'POST',
            data: {
                _auth: initData
            },
            dataType: 'json',
            success: function (result) {
                if (result.ok) {
                    var counterElement = document.getElementById('coins');
                    counterElement.textContent = `${formatNumber(result.Coins)} $`
                } else {
                    alert('Unknown error');
                }
            },
            error: function (xhr) {
                alert('Server error');
            }
        });
    }

    getCoins();

    function updateCoin(newCoin, newClicks) {
        if (!initDataUnsafe.query_id) {
            alert('WebViewQueryId not defined');
            return;
        }
        $.ajax('/updateCoin', {
            type: 'POST',
            data: {
                _auth: initData,
            },
            dataType: 'json',
            success: function (result) {
                if (result.ok) {
                    var counterElement = document.getElementById('coins');
                    counterElement.textContent = `${formatNumber(result.Coins)} $`
                    if (result.ClicksReached) {
                        alert(result.ClicksReached)
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

    async function showPlusOneText(event) {
        try {
            var boostData = await getBoostClicks();
            var plusOneText = document.createElement('div');
            var myClicks = document.getElementById('myClicks')
            myClicks.textContent = `${boostData.myClicks} / ${boostData.clicks5min}`
            plusOneText.textContent = `+${boostData.clickCost}`;
            plusOneText.classList.add('plus-one');
            plusOneText.style.position = 'absolute';
            plusOneText.style.left = (event.clientX + 10) + 'px'; // Добавляем смещение относительно курсора
            plusOneText.style.top = (event.clientY - 20) + 'px'; // Добавляем смещение относительно курсора
            document.body.appendChild(plusOneText);

            // Удаляем элемент после задержки
            setTimeout(function() {
                plusOneText.remove();
            }, 1000);
        } catch (error) {
            console.error(error);
        }
    }


    document.querySelector('.image').addEventListener('click', async function () {
        var currentTime = new Date().getTime();

        this.classList.add('pressed');
        var progressBar = document.querySelector('.progress-bar');

        updateCoin();
        await showPlusOneText(event);


        // counterElement.textContent = formatNumber(newCount);

        // function updateProgressBar() {
        //     counterElement.textContent = newCount + " Coins";
        //     progressBar.style.width = ((newProgressCount) / 5000) * 100 + '%';
        // }
        //
        // updateProgressBar();

        setTimeout(() => {
            this.classList.remove('pressed');
        }, 300);
    });

    document.addEventListener('copy', function(event) {
        event.preventDefault();
    });

    document.addEventListener('contextmenu', function(event) {
        event.preventDefault();
    });

    document.addEventListener('dragstart', function(event) {
        event.preventDefault();
    });

});
