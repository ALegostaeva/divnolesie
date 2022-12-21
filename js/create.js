const form = document.querySelector('form');

async function postData() {
    const doc = {
        name: form.name.value.toUpperCase(),
        task: form.task.value,
        next: form.next.value
    };
    console.log('post', form.name.value.toUpperCase());
    const response = await fetch('https://my-json-server.typicode.com/alegostaeva/alegostaeva-dbBooks/cells', {
      method: 'POST', 
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(doc) // body data type must match "Content-Type" header
    });
    return response.json(); // parses JSON response into native JavaScript objects
  }


const createPost = async (e) => {
    e.preventDefault();

    console.log('create', form.name.value,e);
    console.log('get', isNaN('https://my-json-server.typicode.com/alegostaeva/alegostaeva-dbBooks/cells?name='+ form.name.value));
    const doc = {
        name: form.name.value.toUpperCase(),
        task: form.task.value,
        next: form.next.value
    };
    const response = await fetch('https://my-json-server.typicode.com/alegostaeva/alegostaeva-dbBooks/cells', {
        method: 'POST',
        body: JSON.stringify(doc),
        headers: { 'Content-Type': 'application/json' }
    });
    return response.json();
    //window.location.replace('list.html');
}
form.addEventListener('submit', createPost);
console.log('here',form.name.value);
//form.addEventListener('submit', postData);