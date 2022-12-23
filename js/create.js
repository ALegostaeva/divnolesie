const form = document.querySelector('form');

const createCell = async (e) => {
    e.preventDefault();

    console.log('create', form.name.value,e);
    console.log('get', isNaN('https://my-json-server.typicode.com/alegostaeva/alegostaeva-dbBooks/cells?name='+ form.name.value));
    const doc = {
        name: form.name.value.toUpperCase(),
        task: form.task.value,
        next: form.next.value
    };
    const response = await fetch('https://my-json-server.typicode.com/alegostaeva/alegostaeva-dbBooks/cells', {
        method: 'PATCH',
        mode: 'cors',
        body: JSON.stringify(doc),
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }
    });
    console.log(response);
    return response.json();
    //window.location.replace('list.html');
}
form.addEventListener('submit', createCell);
console.log('here',form.name.value);
//form.addEventListener('submit', postData);
