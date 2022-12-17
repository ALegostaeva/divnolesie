
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


const canvas = document.getElementById('mainCanvas');
const ctx = canvas.getContext('2d'); 
const a = 2 * Math.PI / 6;
const r = 31;
const linesABC = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O'];

let Hexes = [];

function drawHex (hex, x, y, no) { 
  
  ctx.beginPath();
  for (let i = 0; i < 6; i++) {
    ctx.lineTo(x + hex.r * Math.cos(a * i), y + hex.r * Math.sin(a * i));
  }
  ctx.closePath();
  ctx.strokeStyle = 'green';
  //ctx.font = "20px Arial";
  ctx.lineWidth = 0;
  //ctx.fillText(no, x-12, y+9);
  ctx.stroke()
};

const coords = document.querySelector('#mainCanvas');

const getCoords = (event) => {
  const container = canvas.getBoundingClientRect();
  const x = (event.clientX - container.left);
  const y = (event.clientY - container.top);

  coords.textContent = `${x}, ${y}`;
  console.log("click on rect,", {x}, {y});
  console.log("call pixel_to_hex", pixel_to_hex(x,y));
};

ctx.canvas.addEventListener('click', getCoords);

function pixel_to_hex(x,y)
{
    var size = Point(870.0, 1400.0);
    var origin = Point(870.0, 31.5);
    for (const i in Hexes) {
        console.log("Define Hex 1:",Hexes[i].name, Hexes[i].centerX, Hexes[i].centerY);
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

        console.log("is inside; ",r, x1, y1, py1, p_angle_01, p_angle_20, p_angle_03, p_angle_12, p_angle_32, is_inside_1, is_inside_2, );

        if (is_inside_1 || is_inside_2) {
          openDescription(Hexes[i].name);
          return Hexes[i].name;
        }
    };
    let col = x / 30;
    let r = -1.0 / 3.0 * x + Math.sqrt(3.0) / 3.0 * y;
    console.log("Define Hex 2:" ,col, x, y);
    return true;
};

function openDescription(address){
  console.log((address));
  let pageDescription = window.open("pages/info.html?id="+ address, address);
  pageDescription.window.open()
};


function drawMap(lines, colomns, r) {

  var no = 1;
  var abcNo = 0;
  for (let y = r+13; y + r * Math.sin(a) < colomns; y += 38+r * Math.cos(a)) {
    console.log(y, r,y + r * Math.sin(a), y += r * Math.sin(a), 'here1');
    for (let x = r + 20, j = 1; x + r * (1 + Math.cos(a)) < lines ; x += r * (1 + Math.cos(a)), y += (-1) ** j++ * r * Math.sin(a)) {
      var cellName = linesABC[abcNo] + no;
      hexCurrent = new Hex(r,cellName, no, linesABC[abcNo], x, y);
      Hexes.push(hexCurrent);
      drawHex(hexCurrent, x, y, cellName);
      console.log('drawHex',hexCurrent.name,x,y,j);
      no+=1;
    };
    no = 1;
    abcNo += 1;
  };
};

let map = new Image();
map.src = 'assets/map.jpg';
map.onload = function(){
  ctx.drawImage(map,0,0,canvas.width, canvas.height);  
  drawMap(canvas.width, canvas.height, r); 
};
console.log("hexes:" ,Hexes);