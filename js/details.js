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

    if ( cell.img == "") {
        cell.img = "../assets/a1.png"
    };

    let template = `
        <img class="cellImg" src="${cell.img}" style="height:100px" alt="Изображение соты">
        <div class="body-details">
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

// Menu
const body = document.querySelector('body');
const menuOpener = document.querySelector('[data-js-menu]');
const menuIcon = menuOpener.querySelector('.fa');

menuOpener.addEventListener('click', function () {
	menuIcon.classList.toggle('fa-bars');
	menuIcon.classList.toggle('fa-times');

	console.log(body);
	body.classList.toggle('-menu-open');
});