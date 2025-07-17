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
        localStorage.removeItem('vk_user_time');
      
        // Показываем оверлей
        const overlay = document.createElement('div');
        overlay.id = 'loginOverlay';
        overlay.style = `
          position: fixed;
          z-index: 9999;
          top: 0; left: 0;
          width: 100vw; height: 100vh;
          background: rgba(0, 0, 0, 0.9);
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-direction: column;
        `;

        const message = document.createElement('p');
        message.innerText = 'Для продолжения авторизуйтесь через ВКонтакте';
        message.style = 'margin-bottom: 2em; font-size: 1.2em;';

        const vkContainer = document.createElement('div');
        vkContainer.id = 'vk_container';

        overlay.appendChild(message);
        overlay.appendChild(vkContainer);
        document.body.appendChild(overlay);

        // Подключаем VK SDK
        const sdkScript = document.createElement('script');
        sdkScript.src = 'https://unpkg.com/@vkid/sdk@3.0.0/dist-sdk/umd/index.js';
        sdkScript.onload = function () {
          const authScript = document.createElement('script');
          authScript.src = 'js/auth.js';
          document.body.appendChild(authScript);
        };
        document.body.appendChild(sdkScript);

        console.log('here2');
      }      
  })();