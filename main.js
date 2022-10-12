
class Hex {
  constructor(r, name, col, row) {
      this.r = r;
      this.name = name;
      this.col = col;
      this.raw = row
  }

  name (){
    return this.name;
  };

  coords(){
    return (this.col, this.raw)
  }
  
};



const canvas = document.getElementById('mainCanvas');
const ctx = canvas.getContext('2d'); 
const a = 2 * Math.PI / 6;
const r = 31;
const linesABC = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O'];

var Hexs = [];

function drawHex (hex, x, y, no) { 
  
  ctx.beginPath();
  for (var i = 0; i < 6; i++) {
    ctx.lineTo(x + hex.r * Math.cos(a * i), y + hex.r * Math.sin(a * i));
  }
  ctx.closePath();
  ctx.strokeStyle = 'green';
  ctx.font = "20px Arial";
  ctx.lineWidth = 5;
  ctx.fillText(no, x-12, y+9);
  ctx.stroke();
  //ctx.onClick = function() { ctx.fillStyle = 'green'; };
  /*ctx.addEventListener('click', function() {
    if (ctx.isPointInPath()) {
      ctx.fillStyle = 'green';
      ctx.fill();
    }
    else {
      ctx.fillStyle = 'red';
      ctx.fill();
    }
  }, false);*/
  /*ctx.canvas.addEventListener('click',function(no) {
    this.style.backgroundColor = "red";
    console.log("click1", no);
  }, false);*/
};

function windowToCanvas(canvas, x, y) {
  var bbox = canvas.getBoundingClientRect();
  return { x: x - bbox.left * (canvas.width  / bbox.width),
           y: y - bbox.top  * (canvas.height / bbox.height)
         };
}

function clickOnRect(event){

}



function drawMap(lines, colomns, r) {

  var no = 1;
  var abcNo = 0;
  for (let y = r+13; y + r * Math.sin(a) < colomns; y += 38+r * Math.cos(a)) {
    console.log(y, r,y + r * Math.sin(a), y += r * Math.sin(a), 'here1');
    for (let x = r + 20, j = 1; x + r * (1 + Math.cos(a)) < lines ; x += r * (1 + Math.cos(a)), y += (-1) ** j++ * r * Math.sin(a)) {
      var cellName = linesABC[abcNo] + no;
      hexCurrent = new Hex(r,cellName, no, linesABC[abcNo]);
      Hexs.push(hexCurrent);
      drawHex(hexCurrent, x, y, cellName);
      console.log(hexCurrent.name,x,y,j, 'here2');
      no+=1;
    };
    no = 1;
    abcNo += 1;
  };
};

let map = new Image();
map.src = 'src/map.jpg';
map.onload = function(){
  ctx.drawImage(map,0,0,canvas.width, canvas.height);  
  drawMap(canvas.width, canvas.height, r); 
};
