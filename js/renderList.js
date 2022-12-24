//Формирование списка информации о ячейках в админке

const list = document.querySelector('.list');
const searchForm = document.querySelector('.search');

// поиск. не работает
searchForm.addEventListener('submit', e => {
    e.preventDefault();
    renderList(searchForm.term.value.trim())
})

// рендер списка ячеек в админке
const renderList = async (term) => {
    let uri = 'https://my-json-server.typicode.com/alegostaeva/alegostaeva-dbBooks/cells?_sort=name&_order=desc';
    if (term) {
        uri += `&q=${term}`;
    };
    const res = await fetch(uri);
    const data = await res.json();
    let template = '';
    data.forEach(cell => {
        console.log(cell.name);
        template += `
            <div class="post">
                <h1>${cell.name}</h1>
                <p>${cell.task}</p>
                <a href="cell.html?id=${ cell.name }" title = "${ cell.name }">Редактировать</a>
            </div>
        `
    });
    list.innerHTML += template;
}

window.addEventListener('DOMContentLoaded', () => renderList());