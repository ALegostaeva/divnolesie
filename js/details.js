//Страница с информацией по ячейке для пользователя

const id = new URLSearchParams(window.location.search).get('id');
const container = document.querySelector('.details');

const getDetails = async () => {
    const res = await fetch(`https://divnolesie.pages.dev/data/db.json`);
    const cells = await res.json();
    let cell = await cells.find( cell => cell.name === id);
    

    locKey = cell.loc;
    switch (locKey) {
        case "Снежный перевал":
            cell.class='snow';
            cell.color = "#2d3c51";
            cell.bckg = "radial-gradient(67.84% 58.16% at 50% 41.84%, rgba(200, 254, 251, 1) 0%, rgba(45, 60, 81, 1) 60.94%)";
            cell.textColor = '#646464';
            cell.horizon = '../assets/hor_snow.png';
            break;
        case "Пустыня":
            cell.class='desert';
            cell.color = "#e9b973";
            cell.bckg = "radial-gradient(50% 64.75% at 50% 35.25%, #6D7880 0%, #1D2F36 100%)";
            cell.textColor = 'white';
            cell.horizon = '../assets/hor_desert.png';
            break;
        case "Междумирье":
            cell.class='fireflies';
            cell.color = "#154225";
            cell.bckg = 'radial-gradient(50% 64.75% at 50% 35.25%, rgba(238, 238, 160, 1) 0%, rgba(28, 73, 60, 1) 100%)';
            cell.horizon = '../assets/hor_fireflies.png';
            createFireflies();
            break;
        case "Мавкино болото":
            cell.class='rain';
            cell.color = "#244530";
            cell.bckg = 'radial-gradient(47.28% 53.35% at 50% 46.65%, rgba(243, 255, 247, 1) 0%, rgba(91, 106, 122, 1) 100%)';
            cell.horizon = '../assets/hor_boloto.png';
            createRain();
            break;
        case "Каменное плато":
            cell.class='stones';
            cell.color = "#09090F";
            cell.bckg = "radial-gradient(50% 64.75% at 50% 35.25%, rgba(238, 170, 231, 1) 0%, rgba(32, 49, 59, 1) 100%)";
            cell.textColor = 'white';
            cell.horizon = '../assets/hor_stones.png';
            break;
        default:
            cell.class='fireflies';
            cell.color = "#154225";
            cell.bckg = 'radial-gradient(50% 64.75% at 50% 35.25%, rgba(238, 238, 160, 1) 0%, rgba(28, 73, 60, 1) 100%)';
            cell.horizon = '../assets/hor_fireflies.png';
            createFireflies();
    }



    let template = `
        <div class='card-image'>
            <img class="horizon horizon-${cell.class}" src="${cell.horizon}">
        </div>
        

        <div class="body-details body-${cell.class}">
            <div class='location'><span class="fa fa-map-marker location" labels="${cell.loc}"></span><span>${cell.loc}</span></div>
            <h2 class="name_cell">${cell.name}</h2>
            <p class="task">${cell.task}</p><br/>
            <p>Следующий ход возможен на одну из сот:</p>
        </div>
        `
    
    container.innerHTML = template;

    //add weather effect
    let cellWeather = document.getElementById('cell-weather');
    cellWeather.classList.add(cell.class);

    //change body background color
    let b = document.getElementsByTagName('body')[0];
    document.body.style.color.background = cell.bckg;
    b.style.background = cell.bckg;

    //change color of the header and footer
    let h = document.getElementsByTagName('h1')[0];
    h.style.color = 'white';
    let burger = document.getElementsByClassName('site-menu__button')[0];
    burger.style.color = 'white';
    let f = document.getElementsByTagName('small')[0];
    f.style.color = 'white';

    //add image in the cell if it exist
    if (cell.img !=='') {
        let c = document.getElementsByClassName('card-image')[0];
        let addedImg = document.createElement('img');
        addedImg.src = cell.img;
        addedImg.alt = "Изображение соты";
        addedImg.classList.add("cellImg");
        c.appendChild(addedImg);
    }

    //add links to next steps
    let nextSteps = document.createElement('div');
    nextSteps.className = "next-steps";

    for ( const i in cell.next ) {
        const el = document.createElement("a");
        el.textContent = cell.next[i];
        el.href="info.html?id="+ cell.next[i];
        el.className = "next-steps-links";
        el.style.content = cell.next[i];
        console.log(el, el.href);
        nextSteps.appendChild(el)
    }
    console.log(nextSteps);
    container.appendChild(nextSteps);

}

window.addEventListener('DOMContentLoaded', () => getDetails());

//loader
window.onload(function(){
    setTimeout(removeLoader, 2000); //wait for page load PLUS two seconds.
  });
function removeLoader(){
    $( ".hex-loader" ).fadeOut(500, function() {
      // fadeOut complete. Remove the loading div
      $( ".hex-loader" ).remove(); //makes page more lightweight 
  });   
}

//rain

function randRange( minNum, maxNum) {
  return (Math.floor(Math.random() * (maxNum - minNum + 1)) + minNum);
}
function createRain() {
    let nbDrop = 60; 

	for( i=1;i<nbDrop;i++) {
        let dropLeft = randRange(0,100);
        let dropTop = randRange(-100,100);

        let drop = document.createElement('div');
        drop.classList.add('drop');
        drop.id = "drop" + i;

        document.getElementById('cell-weather').append(drop);
        drop.style.left=dropLeft + 'vw';
        drop.style.top=dropTop + 'vw';
        console.log('drops',dropTop,dropLeft)
	}

}

//fireflies
function createFireflies(){
    for( i=1;i<100;i++) {


        let fly = document.createElement('div');
        fly.classList.add('firefly');

        document.getElementById('cell-weather').append(fly);
	}
}