const form = document.querySelector('form');
const createPost = async (e) => {
    e.preventDefault();

    let n = form.name.value;
    let nA = n.toUpperCase();
    const doc = {
        name: nA,
        task: form.task.value
    };
    await fetch('https://my-json-server.typicode.com/alegostaeva/alegostaeva-dbBooks/cells', {
        method: 'POST',
        body: JSON.stringify(doc),
        headers: { 'Content-Type': 'application/json' }
    });
    window.location.replace('list.html');
}
form.addEventListener('submit', createPost);