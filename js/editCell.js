//Редактирование ячейки. Не работает пока не найду хостинг с БД
//TODO посмотреть Firebase


const id = new URLSearchParams(window.location.search).get('id');
const container = document.querySelector('.details');

const getDetails = async () => {
    const res = await fetch(`https://my-json-server.typicode.com/alegostaeva/alegostaeva-dbBooks/cells?name=${id}`);
    const cell = await res.json();

    console.log('get  details',cell);
    const template = `
        
        <input type="text" name="name" required placeholder="Название ячейки(на англ.)" value='${cell[0].name}'>
        <textarea name="task" required placeholder="Описание">${cell[0].task}</textarea>
        <button>Сохранить</button>
        `

        container.innerHTML = template;
}

const form = document.querySelector('form');

const editCell = async (e) => {
    e.preventDefault();

    const res = await fetch(`https://my-json-server.typicode.com/alegostaeva/alegostaeva-dbBooks/cells?name=${id}`);
    const cell = await res.json();

    console.log('edit  details',cell);
    const doc = {
        name: container.name.value.toUpperCase(),
        task: container.task.value,
        //next: container.next.value
    };
    const response = await fetch('https://my-json-server.typicode.com/alegostaeva/alegostaeva-dbBooks/cells/'+cell[0].id, {
        method: 'PUT',
        mode: 'cors',
        body: JSON.stringify(doc),
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }
    });
    console.log(response);
    return response.json();
    //window.location.replace('list.html');
}
container.addEventListener('submit', editCell);

window.addEventListener('DOMContentLoaded', () => getDetails());