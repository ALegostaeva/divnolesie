function showLostConnectionMessage() {
  document.body.innerHTML = `
    <div style="
      display:flex;
      flex-direction:column;
      justify-content:center;
      align-items:center;
      height:100vh;
      background:linear-gradient(to bottom, #1b1b1b, #000);
      color:#fff;
      font-family: 'Cinzel', serif;
      text-align:center;
      padding:20px;
    ">
      <h2>🔮 Потеряна связь с Дивнолесьем</h2>
      <p>Мы ищем ближайший портал, чтобы восстановить магический канал.</p>
      <p>✨ Путник, загляни позже — портал скоро откроется снова!</p>
    </div>
  `;
}

async function isParticipant() {
  
  try {
    var id = localStorage.getItem('vk_user_id');
    const res = await fetch('https://sashadiv.pythonanywhere.com/static/stats.json',{ cache: 'no-cache' });
    //const res = await fetch('../static/stats.json', { cache: 'no-cache' } );
    if (!res.ok) {
      showLostConnectionMessage();
      return false;
    }
    const stats = await res.json();
    const user = stats.find(p => Number(p.vk_id) === Number(id));

    if (!user) return false;

    // ✅ Админ всегда авторизуется
    if (user.admin) return true;

    return user?.is_participant || false; 
  } catch (err) {
    showLostConnectionMessage();
    console.error('Ошибка при загрузке stats:', err);
  }
};

function showLoginOverlay() {  
      
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

          if (!data || !vkid) {
              showDeniedMessage();
              return;
          }
          localStorage.setItem('vk_user_id', vkid);
        
          try {
            const isAuth = await isParticipant();
            if (isAuth) {
              // Прячем оверлей и загружаем страницу без reload
              document.getElementById('loginOverlay').style.display = 'none';
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

window.addEventListener('DOMContentLoaded', async () => {
  // 1. Проверка авторизации до загрузки тяжёлого контента
  const isAuth = await isParticipant();
  if (!isAuth) {
    showLoginOverlay();
    return false;
  }
  return true;  
});