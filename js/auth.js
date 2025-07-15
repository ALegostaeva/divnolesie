// === auth.js ===
// 1. Проверка инициализации VK SDK и запуск авторизации, если нужно
if ('VKIDSDK' in window) {
    console.log('vk auth');
    const VKID = window.VKIDSDK;
  
    VKID.Config.init({
      app: 53901589,
      redirectUrl: 'https://alegostaeva.github.io/divnolesie/',
      responseMode: VKID.ConfigResponseMode.Callback,
      source: VKID.ConfigSource.LOWCODE,
      scope: '',
    });
  
    const oneTap = new VKID.OneTap();
  
    oneTap.render({
      container: document.currentScript.parentElement,
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
      const vkid = data.user.id;
  
      try {
        const res = await fetch('/static/stats.json');
        const stats = await res.json();
  
        const user = stats.find(p => p.vk_id === vkid);
        if (user && user.is_participant) {
          const now = new Date();
          localStorage.setItem('vk_user_id', vkid);
          localStorage.setItem('vk_user_date', now.toISOString());
          console.log('user authorized', vkid, now.toISOString())
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
      console.error('VK ERROR', error);
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
  