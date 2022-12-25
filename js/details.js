//Страница с информацией по ячейке для пользователя

const id = new URLSearchParams(window.location.search).get('id');
const container = document.querySelector('.details');

const getDetails = async () => {
    const res = await fetch(`https://alegostaeva.github.io/data/db.json`);
    const cells = await res.json();
    
    let cell = cells.find( cell => cell.name === id);

    console.log(cell);

    if ( cell.img == "") {
        cell.img = "../assets/a1.png"
    };

    let template = `
        <img src="${cell.img}" style="height:100px" alt="Изображение соты">
        <span class="fa fa-map-marker location"></span><p>${cell.loc}</p>
        <h2 class="name_cell">${cell.name}</h2>
        <p class="task">${cell.task}</p><br/>
        <p>Следующий ход возможен на одну из сот:</p>
        `
    
        container.innerHTML = template;
    
    let nextSteps = document.createElement('div');
    nextSteps.className = "next-steps";
    //document.getElementsByClassName("next-steps");

    for ( const i in cell.next ) {
        const el = document.createElement("a");
        el.textContent = cell.next[i];
        el.href = "info.html?id="+ cell.next[i];
        el.className = "next-steps-links";
        console.log(el);
        nextSteps.appendChild(el)
    }
    console.log(nextSteps);
    container.appendChild(nextSteps);
}

window.addEventListener('DOMContentLoaded', () => getDetails());


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