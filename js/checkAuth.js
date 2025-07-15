(function () {
    var userId = localStorage.getItem('vk_user_id');
    var lastAuthDate = localStorage.getItem('vk_user_date');
  
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
        return savedTime >= seasonStart;
      }
  
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
      
        // Загружаем вручную VK-авторизацию
        const script1 = document.createElement('script');
        script1.src = 'https://vk.com/js/api/openapi.js?169';
        document.body.appendChild(script1);

        const script2 = document.createElement('script');
        script1.src = 'https://id.vk.com/sdk.js';
        document.body.appendChild(script2);

        var script3 = document.createElement('script');
        script3.src = 'js/auth.js';
        document.body.appendChild(script3);
      }      
  })();
  