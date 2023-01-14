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

    switch (cell.loc) {
        case "Снежный перевал":
            cell.weather = "snow";
            console.log("2",cell.weather);
            break;
        case "Пустыня":
            cell.weather = "snow";
            break;
        case "Междумирье":
            cell.weather = "pollen";
            break;
        case "Мавкино болото":
            cell.weather = "rain";
            break;
        case "Каменное плато":
            cell.weather = "";
            break;
        default:
            cell.weather = "";
    }


    if ( cell.img == "")  {
        
        switch (cell.loc) {
            case "Снежный перевал":
                cell.img = "../assets/a/a1.png";
                cell.weather = "snow";
                console.log("2",cell.weather);
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
        <div class="body-details">
            <div class=${cell.weather}></div>
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
        const el = document.createElement("button");
        el.textContent = cell.next[i];
        el.href = "info.html?id="+ cell.next[i];
        el.className = "next-steps-links";
        el.style.content = cell.next[i];
        console.log(el);
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
