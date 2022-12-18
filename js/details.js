const id = new URLSearchParams(window.location.search).get('id');
const container = document.querySelector('.details');
const deleteBtn = document.querySelector('.delete');

const getDetails = async () => {
    const res = await fetch(`http://localhost:3000/cells?name=${id}`);
    const cell = await res.json();
    console.log(id,cell[0].id);

    const template = `
        <img src=${cell[0].img} height=100px>
        <h1>${cell[0].name}</h1>
        <p>${cell[0].task}</p>
        
        `
    console.log(template);
        container.innerHTML = template;
}

window.addEventListener('DOMContentLoaded', () => getDetails());