//Страница с информацией по ячейке для пользователя

const id = new URLSearchParams(window.location.search).get('id');
const container = document.querySelector('.details');

const getDetails = async () => {
    const res = await fetch(`https://my-json-server.typicode.com/alegostaeva/alegostaeva-dbBooks/cells?name=${id}`);
    const cell = await res.json();

    const template = `
        <img src=${cell[0].img} height=100px>
        <h1>${cell[0].name}</h1>
        <p>${cell[0].task}</p>
        `

        container.innerHTML = template;
}

window.addEventListener('DOMContentLoaded', () => getDetails());