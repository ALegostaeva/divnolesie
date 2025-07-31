async function loadProfile() {
    const profileDiv = document.getElementById('profile');
    let stats, info, artefactsDict = {}, unicornData = [];

    try {
        [stats, info, artefactsDict, unicornData] = await Promise.all([
            //fetch('https://sashadiv.pythonanywhere.com/static/stats.json', { cache: 'no-cache' });
            //fetch('https://sashadiv.pythonanywhere.com/static/info_marathon.json');
            //fetch('https://sashadiv.pythonanywhere.com/static/artefacts.json');
            fetch('../static/stats.json', { cache: 'no-cache' }).then(r => r.json()),
            fetch('../static/info_marathon.json').then(r => r.json()),
            fetch('../static/artefacts.json').then(r => r.ok ? r.json() : {}),
            fetch('../static/unicorns.json').then(r => r.ok ? r.json() : [])
        ]);
    } catch (e) {
            profileDiv.innerHTML = '<p>Хм. Здесь явно что-то должно быть, но мы не можем найти. Обещаем поискать. Приходите позже.</p>';
            return;
    }

    const userId = localStorage.getItem('vk_user_id');
    const currentUser = stats.find(p => Number(p.vk_id) === Number(userId));
    if (!currentUser) {
        profileDiv.innerHTML = '<p>Упс. Что-то пошло не так и мы потеряли информацию о вас. Мы поишем в наших архивах, приходите позже.</p>';
        return;
    }

    const curSeason = info.current_season;
    const kurator = stats.find(p => Number(p.vk_id) === Number(currentUser.kurator));

    const artefactCounts = groupByCount(currentUser.artefacts);
    const eggCounts = groupByCount(currentUser.eggs || []);
  
    profileDiv.innerHTML = `
      <h2 style="font-size:2rem">${currentUser.first_name}</h2>
      <p>Куратор: ${kurator ? kurator.first_name + ' ' + kurator.last_name : '—'}</p>
      <p>🪙 ${currentUser.coins} юникоинов</p>
  
      <div class="section">
        <h3>АРТЕФАКТЫ</h3>
        <div class="artifact-grid">
          ${renderArtefacts(artefactCounts, artefactsDict)}
        </div>
      </div>
  
      <div class="section">
        <h3>ЕДИНОРОГИ</h3>
        <div class="group">
          ${renderEggs(currentUser.exp_egg, eggCounts, unicornData)}
        </div>
        <div class="group">
          <strong>Единороги-малыши (2 стадия):</strong>
          ${renderUnicorns(currentUser.unicorns_baby, unicornData, 'baby',currentUser)}
        </div>
        <div class="group">
          <strong>Взрослые единороги (3 стадия):</strong>
          ${renderUnicorns(currentUser.unicorns, unicornData, 'adult', currentUser)}
        </div>
      </div>
  
      <div class="section">
        <h3>Завершенные сезоны</h3>
        ${renderWonSeasons(currentUser.won_seasons)}
      </div>
    `;
  }
  
  function groupByCount(array) {
    return array?.reduce((acc, id) => {
      acc[id] = (acc[id] || 0) + 1;
      return acc;
    }, {}) || {};
  }
  
  function renderArtefacts(counts, dict) {
    if (!Object.keys(counts).length) return '<p>Пока здесь пусто</p>';
    return Object.entries(counts).map(([id, count]) => {
      const a = dict[id] || { name: `Арт. #${id}`, img: '../assets/artefacts/default.png', description: '' };
      return `
        <div class="artifact-card" title="${a.description}">
          <img src="${a.img}" class="artifact-img" alt="${a.name}" />
          <div>${a.name}</div>
          ${count > 1 ? `<div class="artifact-qty">×${count}</div>` : ''}
        </div>`;
    }).join('');
  }
  
  function renderEggs(exp, eggCounts, data) {
    const hasData = Array.isArray(data) && data.length > 0;
    const eggList = Object.entries(eggCounts).map(([id, count]) => {
      const egg = hasData ? data.find(e => e.id === Number(id)) : null;

      const imgSrc = egg?.img ? `${egg.img}` : '../assets/unicorns/egg_default.png';

      const eggName = egg?.name || `Яйцо #${id}`;

      return `
        <div class="egg-card">
          <img src="${imgSrc}" class="egg-img" alt="${eggName}" />
          ${count > 1 ? `<div class="uni-count">×${count}</div>` : ''}
          <div class="egg-label">${eggName}</div>
        </div>`;
    }).join('');
    return `
      <div class="egg-header">
        <h3>Волшебные яйца</h3>
        <div class="egg-exp">ОПЫТ <span>${exp || 0}</span></div>
      </div>
      <div class="egg-grid">${eggList || '<p>Пока здесь пусто</p>'}</div>`;
  }
  
  function renderUnicorns(list = [], unicornData = [], stage = 'baby',currentUser) {
    const counts = list.reduce((acc, id) => {
      acc[id] = (acc[id] || 0) + 1;
      return acc;
    }, {});
  
    const hasData = Array.isArray(unicornData) && unicornData.length > 0;
  
    const grid = Object.entries(counts).map(([id, count]) => {
      const u = hasData ? unicornData.find(e => e.id === Number(id)) : null;

      const defaultImg = stage === 'baby'
      ? '../assets/unicorns/uni_baby_default.png'
      : '../assets/unicorns/unicorn_default.png';

      const imgSrc = u?.img || defaultImg;
  
      const name = u?.name || `${stage === 'baby' ? 'Юн.' : 'Ед.'} #${id}`;

      let expLine = '';
      if (stage === 'baby') {
        const type = u?.type;
        const expField = type ? `exp_${type}` : null;
        const expValue = expField && currentUser[expField];
        expLine = `<div class="unicorn-exp">ОПЫТ: ${expValue}</div>`;
      }
  
      return `
        <div class="unicorn-card">
          <img src="${imgSrc}" class="unicorn-img" alt="${name}">
          ${count > 1 ? `<div class="uni-count">×${count}</div>` : ''}
          <div class="unicorn-label">${name}</div>
          ${expLine}
        </div>
        `;
    }).join('');
  
    return `
      <div class="unicorn-grid">
        ${grid || '<p>Пока здесь пусто</p>'}
      </div>
    `;
  }

  function renderWonSeasons(seasons = []) {
    if (!Array.isArray(seasons) || seasons.length === 0) {
      return '<p>Пока здесь пусто</p>';
    }
  
    return `
      <div class="trophy-grid">
        ${seasons.map(s => `
          <div class="trophy-card">
            <img src="../assets/trophy.png" alt="Трофей" class="trophy-icon">
            <div class="trophy-label">Сезон №${s}</div>
          </div>
        `).join('')}
      </div>
    `;
  }
  
  

window.addEventListener('DOMContentLoaded', loadProfile);