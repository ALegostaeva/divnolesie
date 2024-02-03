
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


function Point(x, y) {
  return {x: x, y: y};
};

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


// Функция для отрисовки одного гексагона
function drawHex (hex, x, y, no, withText, paths, isPath) { 
  
  ctx.beginPath();
  
  for (let i = 0; i < 6; i++) {
    ctx.lineTo(x + hex.r * Math.cos(a * i), y + hex.r * Math.sin(a * i));
  }
  
  ctx.closePath();

   
  
  if (paths == true){
    if (isPath == true) {
      ctx.strokeStyle = 'rgb(249,249,8,1)';
      ctx.fillStyle = "rgb(249,249,8,0.5)";
      ctx.fill();
    } else {
      ctx.strokeStyle = 'green';
    }
  } else {
    ctx.strokeStyle = 'green';
  }
  
  ctx.lineWidth = 0;
  
  if (withText == true) {
    ctx.font = "20px Arial";
    ctx.fillStyle = "rgba(30,40,0,.5)";
    ctx.fillText(no, x-12, y+9);
  };
  ctx.stroke()
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
  let pageDescription = window.open("pages/info.html?id="+ address,"_top", address);
  //pageDescription.ta
  //pageDescription.window.open()
};


async function drawMap(lines, colomns, r, withText, paths) {

  const res = await fetch(`https://divnolesie.pages.dev/data/db.json`);
  cells = await res.json();

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
      drawHex(hexCurrent, x, y, cellName, withText, paths, isPath);
      no+=1;
    };
    no = 1;
    abcNo += 1;
  };
};



//drawScreen
window.onload = function(){  
  drawMap(canvas.width, canvas.height, r, showLabels, showPaths); 
};


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

const btnContact = document.querySelector('#contact');

btnContact.addEventListener ('click', () => {

}
)