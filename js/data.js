const list = document.querySelector('.list');
const searchForm = document.querySelector('.search');

searchForm.addEventListener('submit', e => {
    e.preventDefault();
    renderList(searchForm.term.value.trim())
})


const renderList = async (term) => {
    let uri = 'http://localhost:3000/cells?_sort=name&_order=desc';
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
                <a href="/details.html?id=${ cell.id }">Read more...</a>
            </div>
        `
    });
    list.innerHTML += template;
}

window.addEventListener('DOMContentLoaded', () => renderList());