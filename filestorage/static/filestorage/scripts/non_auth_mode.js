

// Context sensual pop-up menu

var popup_menu = document.getElementById('info_popup');

var menuActive = menu.getElementsByClassName('menu');
var menu0 = menu.getElementsByClassName('menu0');
var menu2 = menu.getElementsByClassName('menu2');

var back_menu_btn = document.getElementById('back');
back_menu_btn.addEventListener('click', showMenu0);


var more_menu_btn = document.getElementById('more');
more_menu_btn.addEventListener('click', showMenu2);

function menu2PopUp() {
	
	selectModeOn();
	
	let counter = document.getElementById('counter');
	let span = document.createElement('span');
		
	span.innerText = "0 item";
	counter.appendChild(span);
	
	let frames = document.getElementsByClassName('responsive');
	for (let frame of frames) {
		frame.addEventListener('click', countItem);
	}
	
	function countItem() {
		popup_menu.style.display = "block";
		let len = selected.length;
		let msg = "item";
		if (len > 1) { msg = "items";} 
		span.innerText = len + ' ' + msg;
	}
			
	let abort_menu_btn = document.getElementById('abort');
	abort_menu_btn.addEventListener('click', abort);
	function abort() {
		back_menu_btn.click();
		more_menu_btn.click();
	}
	
	back_menu_btn.addEventListener('click', exit);
	function exit() {
			
		for (let frame of frames) {
			frame.removeEventListener('click', countItem);
		}
		span.remove();
		selectModeOff();
		//	Reset a abort and a back 
		abort_menu_btn.removeEventListener('click',abort);
		this.removeEventListener('click',exit);

		
	}
	

}

function showMenu0() {
	for (let e of menuActive) {
		e.style.display = "none";
	}
		
	for (let m of menu0) {
		m.style.display = "inline-block";
	}
	
	popup_menu.style.display = "none";
}




function showMenu2() {
	for (let e of menuActive) {
		e.style.display = "none";
	}
	
	for (let m of menu2) {
		m.style.display = "inline-block";
	}
	
	menu2PopUp();
}

