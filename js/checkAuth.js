(function () {
    console.log('vk auth checker');
    var userId = localStorage.getItem('vk_user_id');
    var lastAuthDate = localStorage.getItem('vk_user_date');
    console.log('vk auth data:',userId, lastAuthDate);
  
    // Сезон считается с 1 числа: сентябрь, декабрь, март, июнь
    function isSeasonValid() {
        const now = new Date();
        const month = now.getUTCMonth(); // 0 — январь
        const day = now.getUTCDate();
    
        // Определяем начало сезона
        let seasonStart;
        if (month >= 8 && month <= 10) {
          seasonStart = new Date(Date.UTC(now.getUTCFullYear(), 8, 1)); // 1 сентября
        } else if (month >= 11 || month === 0) {
          seasonStart = new Date(Date.UTC(month === 11 ? now.getUTCFullYear() : now.getUTCFullYear() - 1, 11, 1)); // 1 декабря
        } else if (month >= 1 && month <= 2) {
          seasonStart = new Date(Date.UTC(now.getUTCFullYear(), 2, 1)); // 1 марта
        } else {
          seasonStart = new Date(Date.UTC(now.getUTCFullYear(), 5, 1)); // 1 июня
        }
    
        // Если время авторизации раньше текущего сезона — сброс
        const savedTimestamp = localStorage.getItem('vk_user_time');
        if (!savedTimestamp) return false;
        const savedTime = new Date(parseInt(savedTimestamp, 10));
        console.log("time checker", savedTime, seasonStart,savedTime >= seasonStart)
        return savedTime >= seasonStart;
      }
    
    console.log("here1",!isSeasonValid(),!userId, !lastAuthDate );
  
    if (!userId || !lastAuthDate || !isSeasonValid()) {
        localStorage.removeItem('vk_user_id');
        localStorage.removeItem('vk_user_date');
      
        // Создаем окно авторизации
        var overlay = document.createElement('div');
        overlay.id = 'loginOverlay';
        overlay.style = 'position:fixed;z-index:999;background:#000000dd;color:#fff;top:0;left:0;width:100vw;height:100vh;display:flex;align-items:center;justify-content:center';
      
        overlay.innerHTML = `
          <div style="text-align:center">
            <p>Для продолжения авторизуйтесь через ВКонтакте</p>
          `;
      
        document.body.innerHTML = ''; // очищаем всё, чтобы не загружалась остальная страница
        document.body.appendChild(overlay);
        console.log("here2" );

        var script1 = document.createElement('script');
        script1.src = 'https://unpkg.com/@vkid/sdk@<3.0.0/dist-sdk/umd/index.js';
        document.body.appendChild(script1);

        var script = document.createElement('script');
        script.src = 'js/auth.js';
        document.body.appendChild(script);
      }      
  })();