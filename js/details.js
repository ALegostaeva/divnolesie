//Страница с информацией по ячейке для пользователя

const id = new URLSearchParams(window.location.search).get('id');
const container = document.querySelector('.details');

const getDetails = async () => {
    const res = await fetch(`https://alegostaeva.github.io/data/db.json`);
    console.log('await get');
    const cells = await res.json();
    console.log('await parse',cells);
    let cell = await cells.find( cell => cell.name === id);

    console.log(cell);
    let cellWeather = document.getElementById('cell-weather');
    

    switch (cell.loc) {
        case "Снежный перевал":
            cellWeather.classList.add('snow');
            cell.color = "#2d3c51";
            break;
        case "Пустыня":
            cellWeather.classList.add('snow');
            cell.color = "#d5aa6f";
            break;
        case "Междумирье":
            cellWeather.classList.add('fireflies');
            cell.color = "#154225";
            createFireflies();
            break;
        case "Мавкино болото":
            cellWeather.classList.add('rain');
            cell.color = "#244530";
            createRain();
            break;
        case "Каменное плато":
            cellWeather.classList.add('rain');
            cell.color = "#3f4044";
            break;
        default:
            cell.color = "#222831";
            cell.weather = "";
    }



    if ( cell.img == "")  {
        switch (cell.loc) {
            case "Снежный перевал":
                cell.img = "../assets/a/a1.png";
                break;
            case "Пустыня":
                cell.img = "../assets/k/k26.png";
                break;
            case "Междумирье":
                cell.img = "../assets/g/g13.png";
                break;
            case "Мавкино болото":
                cell.img = "../assets/k/k3.png";
                break;
            case "Каменное плато":
                cell.img = "../assets/c/c18.png";
                break;
            default:
                cell.img = "../assets/e/e14.png";
                
        }
    };

    let template = `
        <img class="cellImg" src="${cell.img}" style="height:100px" alt="Изображение соты">
        <div class="body-details" style="background-color:${cell.color}">
            <span class="fa fa-map-marker location" labels="${cell.loc}"></span><span class="location">${cell.loc}</span>
            <h2 class="name_cell">${cell.name}</h2>
            <p class="task">${cell.task}</p><br/>
            <p>Следующий ход возможен на одну из сот:</p>
        </div>
        `
    
    container.innerHTML = template;
    
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

    //let bodyDetails = document.getElementsByClassName('details');
    //bodyDetails[0].appendChild(cellWeather);
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
    let nbDrop = 858; 

	for( i=1;i<nbDrop;i++) {
        let dropLeft = randRange(0,100);
        let dropTop = randRange(-100,100);

        let drop = document.createElement('div');
        drop.classList.add('drop');
        drop.id = "drop" + i;

        document.getElementsByClassName('rain')[0].append(drop);
        drop.style.left=dropLeft + 'vw';
        drop.style.top=dropTop + 'vw';
        console.log('drops',dropTop,dropLeft)
	}

}

//fireflies
function createFireflies(){
    for( i=1;i<10;i++) {


        let fly = document.createElement('div');
        fly.classList.add('firefly');

        document.getElementsByClassName('fireflies')[0].append(fly);
	}
}