const list = document.querySelector('.list');
const searchForm = document.querySelector('.search');

searchForm.addEventListener('submit', e => {
    e.preventDefault();
    renderList(searchForm.term.value.trim())
})


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
                <a href="..pages/info.html?id=${ cell.id }" title = "${ cell.name }">Read more...</a>
            </div>
        `
    });
    list.innerHTML += template;
}

window.addEventListener('DOMContentLoaded', () => renderList());