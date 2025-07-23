(function () {
    var userId = localStorage.getItem('vk_user_id');
    var lastAuthDate = localStorage.getItem('vk_user_date');

    async function isParticipant(id) {
      try {
        const res = await fetch('static/stats.json');
        const stats = await res.json();
  
        const user = stats.find(p => Number(p.vk_id) === id);
        return (user && user.is_participant) 
      } catch (err) {
        console.error('Ошибка при загрузке stats:', err);
      }
    }


    // === Если авторизация НЕ нужна — выходим
    if (isParticipant(userId) && lastAuthDate) {
      return;
    }
  
    if (!userId || !lastAuthDate) {
        localStorage.removeItem('vk_user_id');
        localStorage.removeItem('vk_user_date');
        localStorage.removeItem('vk_user_time');
      
        // Показываем оверлей
        const overlay = document.getElementById('loginOverlay');
        overlay.style.display = 'flex';

        const vkContainer = document.getElementById('VkIdSdkOneTap');

        const sdkScript = document.createElement('script');
        sdkScript.src = 'https://unpkg.com/@vkid/sdk@3.0.0/dist-sdk/umd/index.js';
        vkContainer.appendChild(sdkScript);
    
        if ('VKIDSDK' in window) {
          const VKID = window.VKIDSDK;
    
          VKID.Config.init({
            app: 53901589,
            redirectUrl: 'https://alegostaeva.github.io/divnolesie/',
            responseMode: VKID.ConfigResponseMode.Callback,
            source: VKID.ConfigSource.LOWCODE,
            scope: '',
          });

          const oneTap = new VKID.OneTap();

          // Получение контейнера из разметки.
          const container = document.getElementById('VkIdSdkOneTap');

          // Проверка наличия кнопки в разметке.
          if (container) {
            oneTap.render({
              container: container, 
              scheme: 'dark',
              showAlternativeLogin: true
            })
              .on(VKID.WidgetEvents.ERROR, vkidOnError)
              .on(VKID.OneTapInternalEvents.LOGIN_SUCCESS, function (payload) {
                const code = payload.code;
                const deviceId = payload.device_id;
          
                VKID.Auth.exchangeCode(code, deviceId)
                  .then(vkidOnSuccess)
                  .catch(vkidOnError);
              });
        
          async function vkidOnSuccess(data) {
            const vkid = data.user_id;

            if (!data || !data.user_id) {
              console.error('vkidOnSuccess: данные авторизации отсутствуют или некорректны', data);
              showDeniedMessage();
              return;
            }
        
            try {
              const res = await fetch('static/stats.json');
              const stats = await res.json();
        
              const user = stats.find(p => Number(p.vk_id) === vkid);
              if (user && user.is_participant) {
                const now = new Date();
                localStorage.setItem('vk_user_id', vkid);
                localStorage.setItem('vk_user_date', now.toISOString());
                window.location.href = './index.html';
              } else {
                showDeniedMessage();
              }
            } catch (err) {
              console.error('Ошибка при загрузке stats:', err);
              showDeniedMessage();
            }
          }
        
          function vkidOnError(error) {
            showDeniedMessage();
          }
        
          function showDeniedMessage() {
            document.body.innerHTML = `
              <div style="padding: 2em; text-align: center; font-size: 1.2em; color: white; background-color: black">
                <p>🔥 Путник, кажется ты еще не участвуешь в марафоне или мы тебя потеряли.</p>
                <p>Обратись к администраторам марафона в группе <a href="https://vk.com/book_shelf" target="_blank">Книжная полка</a> за помощью.</p>
              </div>
            `;
          }
        }
      }
    }    
})();