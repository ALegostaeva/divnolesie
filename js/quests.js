// Menu
const body = document.querySelector('body');
const menuOpener = document.querySelector('[data-js-menu]');
const menuIcon = menuOpener.querySelector('.fa');

menuOpener.addEventListener('click', function () {
	menuIcon.classList.toggle('fa-bars');
	menuIcon.classList.toggle('fa-times');

	console.log(body);
	body.classList.toggle('-menu-open');
});


const idQuest = new URLSearchParams(window.location.search).get('quest');
const container = document.querySelector('.quest');

