const id = new URLSearchParams(window.location.search).get('id');
const container = document.querySelector('.details');
const deleteBtn = document.querySelector('.delete');

const renderDetails = async () => {
    const res = await fetch(`http://localhost:3000/cells/${id}`);
    console.log(res);
    const cell = await res.json();

    const template = `
        <img src=${cell.img} height=100px>
        <h1>${cell.name}</h1>
        <p>${cell.task}</p>
        
        `
    console.log(template);
        container.innerHTML = template;
}

window.addEventListener('DOMContentLoaded', () => renderDetails());