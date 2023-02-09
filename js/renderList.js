//Формирование списка информации о ячейках в админке

const list = document.querySelector('.list');
const searchForm = document.querySelector('.search');

// поиск. не работает
/*searchForm.addEventListener('submit', e => {
    console.log('search', searchForm.term.value, searchForm.term.value.trim())
    e.preventDefault();
    renderList(searchForm.term.value.trim())
})*/

// рендер списка ячеек в админке
const renderList = async (term) => {
    let uri = 'https://divnolesie.pages.dev/data/db.json';
    if (term) {
        uri += `&q=${term}`;
    };
    const res = await fetch(uri);
    const data = await res.json();
    let template = '';
    data.forEach(cell => {
        console.log(cell.name);
        template += `
            <div class="cell">
                <h2>${cell.name}</h2>
                <p>${cell.task}</p>
                <a href="../pages/info.html?id=${ cell.name }" title = "${ cell.name }">Подробнее</a>
            </div>
        `
    });
    list.innerHTML += template;
}

window.addEventListener('DOMContentLoaded', () => renderList());