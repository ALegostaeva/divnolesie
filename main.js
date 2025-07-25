
class Hex {
  constructor(r, name, col, row, centerX, centerY) {
      this.r = r;
      this.name = name;
      this.col = col;
      this.raw = row;
      this.centerX = centerX;
      this.centerY = centerY;
  }

  name (){
    return this._name;
  };

  get coords (){
    return (this._col, this._raw)
  };

  get centerCoords (){
    return (this.centerX, this.centerY)
  }
  
};

async function loadSeasonInfo() {
  const seasonBox = document.getElementById('seasonInfoBox');
  const currentSeasonEl = document.getElementById('currentSeasonValue');
  const daysEl = document.getElementById('daysToNextSeasonValue');

  try {
    const res = await fetch('./static/info_marathon.json');
    if (!res.ok) throw new Error('Ошибка при загрузке current_season');

    const data = await res.json();

    if (typeof data.current_season === 'number') {
      currentSeasonEl.textContent = data.current_season;
    } else {
      document.getElementById('currentSeasonText').style.display = 'none';
    }

    const now = new Date();
    const year = now.getUTCFullYear();
    const month = now.getUTCMonth(); // от 0 до 11
    const day = now.getUTCDate();

    // Вычисляем ближайшую дату начала следующего сезона:
    const seasonStartDates = [];

    // Определим, какие даты актуальны (в зависимости от месяца)
    if (month <= 1) { // январь-февраль
      seasonStartDates.push(new Date(Date.UTC(year, 2, 1))); // 1 марта
    } else if (month === 11) { // декабрь
      seasonStartDates.push(new Date(Date.UTC(year + 1, 2, 1))); // 1 марта следующего года
    } else {
      seasonStartDates.push(
        new Date(Date.UTC(year, 2, 1)),  // 1 марта
        new Date(Date.UTC(year, 5, 1)),  // 1 июня
        new Date(Date.UTC(year, 8, 1)),  // 1 сентября
        new Date(Date.UTC(year, 11, 1))  // 1 декабря
      );
    }

    const nowUTC = new Date(Date.UTC(year, month, day)); // дата без времени
    const futureDates = seasonStartDates.filter(d => d > nowUTC);
    const nextDate = futureDates.sort((a, b) => a - b)[0];

    if (nextDate) {
      const msPerDay = 1000 * 60 * 60 * 24;
      const daysLeft = Math.ceil((nextDate - nowUTC) / msPerDay);
      daysEl.textContent = daysLeft;
    } else {
      document.getElementById('daysToNextSeasonText').style.display = 'none';
    }

    seasonBox.style.display = 'block';

  } catch (error) {
    console.warn('Не удалось загрузить данные о сезоне:', error);
  }
}


function Point(x, y) {
  return {x: x, y: y};
};

function showTooltip(htmlContent, x, y) {
  tooltip.innerHTML = htmlContent;
  tooltip.style.display = 'block';

  tooltip.style.left = '0px';
  tooltip.style.top = '0px';

  const tooltipRect = tooltip.getBoundingClientRect();
  const pageWidth = window.innerWidth;
  const pageHeight = window.innerHeight;

  let left = x + 15;
  let top = y + 15;

  if (left + tooltipRect.width > pageWidth) {
    left = x - tooltipRect.width - 15;
  }

  if (top + tooltipRect.height > pageHeight) {
    top = y - tooltipRect.height - 15;
  }

  tooltip.style.left = `${left}px`;
  tooltip.style.top = `${top}px`;
}

//переменные для отрисовки канваса
const canvas = document.getElementById('mainCanvas');
const ctx = canvas.getContext('2d'); 
const a = 2 * Math.PI / 6;
const r = 31;
const linesABC = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O'];

let Hexes = [];
let cells = [];
let showLabels = false;
let showPaths = false;
let showCampfires = true; // по умолчанию костёрки включены

let activeCells = new Set(); // клетки, где есть игроки
let statsData = []; // Массив с игроками, нужен для поиска по cellName

let showMyLocation = true;
let myCurrentCell = null; // имя ячейки

let showMyPath = false;
let visitedThisSeason = new Set(); // Массив ячеек, посещённых в этом сезоне

// tooltip
// Создаём и добавляем tooltip div к документу
const tooltip = document.createElement('div');
tooltip.id = 'tooltip';
tooltip.style.position = 'absolute';
tooltip.style.padding = '6px 10px';
tooltip.style.background = 'rgba(30, 30, 30, 0.85)';
tooltip.style.color = '#fff';
tooltip.style.borderRadius = '8px';
tooltip.style.fontSize = '14px';
tooltip.style.pointerEvents = 'none';
tooltip.style.display = 'none';
tooltip.style.zIndex = 1000;
document.body.appendChild(tooltip);

// Функция для отрисовки одного гексагона
function drawHex(hex, x, y, no, withText, paths, isPath, strangers = false, isPlayerHere = false, isVisited = false) {
    ctx.beginPath();
    for (let i = 0; i < 6; i++) {
      ctx.lineTo(x + hex.r * Math.cos(a * i), y + hex.r * Math.sin(a * i));
    }
    ctx.closePath();
  
    if (isPlayerHere) {
      ctx.font = "40px Arial";
      ctx.strokeStyle = 'red';
      ctx.fillStyle = 'rgba(255, 0, 0, 0.3)'; // прозрачный красный
      ctx.fill();
      ctx.fillText("📍", x - 20, y + 8); // символ метки
    } else if (isVisited) {
      ctx.fillStyle = 'rgba(255, 0, 0, 0.2)'; 
      ctx.strokeStyle = 'red';
      ctx.fill();
    } else if (!isPlayerHere && strangers) {
      const gradient = ctx.createRadialGradient(x, y, 5, x, y, hex.r);
      ctx.font = "22px Arial";
      ctx.fillStyle = "orange";
      ctx.fillText("🔥", x - 10, y + 8); // символ костра
      gradient.addColorStop(0, 'rgba(242, 255, 156, 0.6)'); // тёплый центр
      gradient.addColorStop(1, 'rgba(255, 255, 255, 0.1)');   // внешнее свечение
      ctx.fillStyle = gradient;
      ctx.fill();
      for (let i = 0; i < 4; i++) {
        const angle = Math.random() * 2 * Math.PI;
        const radius = 10 + Math.random() * 8;
        const sparkX = x + Math.cos(angle) * radius;
        const sparkY = y + Math.sin(angle) * radius;
        ctx.beginPath();
        ctx.arc(sparkX, sparkY, 1.5, 0, 2 * Math.PI);
        ctx.fillStyle = "rgba(255, 200, 50, 0.8)";
        ctx.fill();
      }
    } else if (paths === true && isPath === true) {
      ctx.strokeStyle = 'rgb(249,249,8,1)';
      ctx.fillStyle = "rgb(249,249,8,0.5)";
      ctx.fill();
    } else {
      ctx.strokeStyle = 'rgb(138, 127, 90)';
    }
  
    ctx.lineWidth = 0;
    
    if (withText == true) {
      ctx.font = "20px Arial";
      ctx.fillStyle = "rgba(30,40,0,.5)";
      ctx.fillText(no, x-12, y+9);
    };
    ctx.stroke();
  };

//функция для получения координат клика пользователя
const coords = document.querySelector('#mainCanvas');

const getCoords = (event) => {
  const container = canvas.getBoundingClientRect();
  const x = (event.clientX - container.left);
  const y = (event.clientY - container.top);

  coords.textContent = `${x}, ${y}`;
  pixel_to_hex(x,y)
  
};

ctx.canvas.addEventListener('click', getCoords);


//функция для определения гексагона, куда был клик
function pixel_to_hex(x,y)
{
    
    for (const i in Hexes) {
        var x1 = Math.abs(x - Hexes[i].centerX);
        var y1 = Math.abs(y - Hexes[i].centerY);

        const r = 31;

        var py1 = r * 0.86602540378;
        var px2 = r * 0.2588190451;
        var py2 = r * 0.96592582628;

        var p_angle_01 = -x1 * (py1 - y1) - x1 * y1;
        var p_angle_20 = -y1 * (px2 - x1) + x1 * (py2 - y1);
        var p_angle_03 = y1 * r;
        var p_angle_12 = -x1 * (py2 - y1) - (px2 - x1) * (py1 - y1);
        var p_angle_32 = (r - x1) * (py2 - y1) + y1 * (px2 - x1);

        var is_inside_1 = (p_angle_01 * p_angle_12 >= 0) && (p_angle_12 * p_angle_20 >= 0);
        var is_inside_2 = (p_angle_03 * p_angle_32 >= 0) && (p_angle_32 * p_angle_20 >= 0);

      
        if (is_inside_1 || is_inside_2) {
          openDescription(Hexes[i].name);
          return Hexes[i].name;
        }
    };
    return false;
};

function openDescription(address){
  window.location.href = "pages/info.html?id=" + address;
};


async function drawMap(lines, colomns, r, withText, paths) {

  //const res = await fetch(`https://divnolesie.pages.dev/data/db.json`);
  const res = await fetch(`./data/db.json`);
  cells = await res.json();

  activeCells.clear(); // очищаем старые активные клетки
  let currentUser = null; 

  let stats = {};
  try {
    const statsRes = await fetch('./static/stats.json');
    if (!statsRes.ok) throw new Error('Ошибка при загрузке stats.json');
    stats = await statsRes.json();
    statsData = stats;
    if (Array.isArray(stats)) {
      for (const p of stats) {
        if (p.is_participant && p.current_cell) {
          activeCells.add(p.current_cell);
        }
      }
    }

  } catch (err) {
    console.error('Ошибка при загрузке статистики:', err);
  }

  // Отображение игрока на карте
  const userId = localStorage.getItem('vk_user_id');
  myCurrentCell = null; // сбрасываем

  if (userId && Array.isArray(stats)) {
    currentUser = stats.find(p => Number(p.vk_id) === Number(userId));
    if (currentUser && currentUser.current_cell) {
      myCurrentCell = currentUser.current_cell;
      document.getElementById('showMyLocation').disabled = false;
    } else {
      document.getElementById('showMyLocation').disabled = true;
    }
  } else {
    document.getElementById('showMyLocation').disabled = true;
  }

  const currentSeason = await fetch('./static/info_marathon.json')
  .then(res => res.ok ? res.json() : null)
  .then(data => data?.current_season)
  .catch(() => null);

  // Сброс пути
  visitedThisSeason.clear();
  showMyPathCheckbox.disabled = true;

  if (userId && currentSeason && Array.isArray(stats)) {
    currentUser = stats.find(p => Number(p.vk_id) === Number(userId));
    if (currentUser?.visited_cells?.[currentSeason]) {
      const allVisited = currentUser.visited_cells[currentSeason];
      const uniqueVisited = [...new Set(allVisited)];
      for (const cell of uniqueVisited) {
        visitedThisSeason.add(cell);
      }
      showMyPathCheckbox.disabled = false;
    }
  }

  var no = 1;
  var abcNo = 0;
  for (let y = r+13; y + r * Math.sin(a) < colomns; y += 38+r * Math.cos(a)) {
    y += r * Math.sin(a);
    for (let x = r + 20, j = 1; x + r * (1 + Math.cos(a)) < lines ; x += r * (1 + Math.cos(a)), y += (-1) ** j++ * r * Math.sin(a)) {
      var cellName = linesABC[abcNo] + no;
      hexCurrent = new Hex(r,cellName, no, linesABC[abcNo], x, y);
      Hexes.push(hexCurrent);
      let cCell = cells.find(cell => cell.name === cellName);
      if (cCell.isPath == true) {
        isPath = true;
      } else {
        isPath = false;
      }
      const hasStrangers = activeCells.has(cellName);
      const isPlayerHere = currentUser?.current_cell === cellName;
      const isVisited = showMyPath && visitedThisSeason.has(cellName) && !isPlayerHere;

      drawHex(hexCurrent, x, y, cellName, withText, paths, isPath, showCampfires && hasStrangers, isPlayerHere, isVisited);
      no+=1;
    };
    no = 1;
    abcNo += 1;
  };
};



//drawScreen
window.onload = function(){  
    drawMap(canvas.width, canvas.height, r, showLabels, showPaths); 
    loadSeasonInfo();
};

const toggleButton = document.getElementById('toggleUIRow');
const uiRow = document.querySelector('.ui-row');
let isHidden = false;

toggleButton.addEventListener('click', () => {
  isHidden = !isHidden;
  uiRow.classList.toggle('hidden', isHidden);
  toggleButton.innerHTML = isHidden ? '▼' : '▲';
  toggleButton.setAttribute('aria-label', isHidden ? 'Показать панель' : 'Скрыть панель');
});


//переменные для управления кнопками "Скрыть/показать названия ячеек"

const btnShowLabels = document.querySelector('#addLabels');

btnShowLabels.addEventListener ('change', () => {
    if (btnShowLabels.checked) {
      showLabels = true;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      drawMap(canvas.width, canvas.height, r, showLabels, showPaths); 
    } else {
      showLabels = false;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      drawMap(canvas.width, canvas.height, r, showLabels, showPaths); 
    }
  }
)

const btnShowPaths = document.querySelector('#showPaths');

btnShowPaths.addEventListener ('change', () => {
  if (btnShowPaths.checked) {
    showPaths = true;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawMap(canvas.width, canvas.height, r, showLabels, showPaths); 
  } else {
    showPaths = false;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawMap(canvas.width, canvas.height, r, showLabels, showPaths); 
  }
}
)

// чекбокс для отображения других игроков
const toggleCampfiresCheckbox = document.getElementById('toggleCampfires');
toggleCampfiresCheckbox.addEventListener('change', () => {
  showCampfires = toggleCampfiresCheckbox.checked;
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawMap(canvas.width, canvas.height, r, showLabels, showPaths);
});

// чекбокс для отображения Игрока
const myLocationCheckbox = document.getElementById('showMyLocation');
myLocationCheckbox.addEventListener('change', () => {
  showMyLocation = myLocationCheckbox.checked;
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawMap(canvas.width, canvas.height, r, showLabels, showPaths);
});

// чекбокс для отображения Пути игрока в этом сезоне
const showMyPathCheckbox = document.getElementById('showMyPath');
showMyPathCheckbox.addEventListener('change', () => {
  showMyPath = showMyPathCheckbox.checked;
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawMap(canvas.width, canvas.height, r, showLabels, showPaths);
});

const btnContact = document.querySelector('#contact');

//btnContact.addEventListener ('click', () => {})

// HOVER (десктоп)
canvas.addEventListener('mousemove', (e) => {
  const rect = canvas.getBoundingClientRect();
  const mouseX = e.clientX - rect.left;
  const mouseY = e.clientY - rect.top;

  let found = false;
  for (const hex of Hexes) {
    const dx = mouseX - hex.centerX;
    const dy = mouseY - hex.centerY;
    const distance = Math.sqrt(dx * dx + dy * dy);
    if (distance <= r) {
      const playersOnHex = statsData.filter(p => p.current_cell === hex.name && p.is_participant);
      if (playersOnHex.length > 0) {
        const html = playersOnHex.map(p => `🦄 ${p.first_name} ${p.last_name}`).join('<br>');
        showTooltip(html, e.pageX, e.pageY);
        found = true;
        break;
      }
    }
  }

  if (!found) {
    tooltip.style.display = 'none';
  }
});

canvas.addEventListener('mouseleave', () => {
  tooltip.style.display = 'none';
});

// TOUCH (мобилка)
let touchTimeout = null;
canvas.addEventListener('touchstart', (e) => {
  const touch = e.touches[0];
  const rect = canvas.getBoundingClientRect();
  const x = touch.clientX - rect.left;
  const y = touch.clientY - rect.top;

  touchTimeout = setTimeout(() => {
    for (const hex of Hexes) {
      const dx = x - hex.centerX;
      const dy = y - hex.centerY;
      if (Math.sqrt(dx * dx + dy * dy) < r) {
        const playersOnHex = statsData.filter(p => p.current_cell === hex.name && p.is_participant);
        if (playersOnHex.length > 0) {
          const html = playersOnHex.map(p => `👤 ${p.first_name} ${p.last_name}`).join('<br>');
          showTooltip(html, touch.pageX, touch.pageY);
        }
      }
    }
  }, 600);
});

canvas.addEventListener('touchend', () => {
  clearTimeout(touchTimeout);
  tooltip.style.display = 'none';
});

window.addEventListener('load', function () {
  const loader = document.getElementsByClassName('hex-loader')[0];
  console.log('loader hide', loader);
  if (loader) {
    loader.style.display = 'none';
  }
});
