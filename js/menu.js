const body = document.querySelector('body');
const menuOpener = document.querySelector('[data-js-menu]');
const menuIcon = menuOpener.querySelector('.fa');
console.log('menu vars', body, menuOpener, menuIcon);

menuOpener.addEventListener('click', function () {
    console.log('tap menu');
    menuIcon.classList.toggle('fa-bars');
    menuIcon.classList.toggle('fa-times');
    body.classList.toggle('-menu-open');
});