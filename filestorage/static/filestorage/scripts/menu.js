//	menu.js

/*	Create a new directory	*/

var createDirBtn = document.getElementById('new-directory');
var modalMakeDir = document.getElementById("newDirModal");

// Get the <span> element that closes the modal
var closeMakeDirModalBtn = document.getElementsByClassName("newDirModal-close")[0];

// When the user clicks the button, open the modal 
createDirBtn.onclick = function() {
  modalMakeDir.style.display = "block";
}

// When the user clicks on <span> (x), close the modal
closeMakeDirModalBtn.onclick = function() {
  modalMakeDir.style.display = "none";
  back_menu_btn.click();
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
  if (event.target == modalMakeDir) {
    modalMakeDir.style.display = "none";
    back_menu_btn.click();
  }
}

var newDirAcceptBtn = document.getElementsByClassName("newDirModal-accept")[0];
newDirAcceptBtn.addEventListener('click', createNewDirectory);

function createNewDirectory() {
	newDirForm =  document.forms['newDirForm'];
	var formData = new FormData(newDirForm);
	
	var myInit = { 	method: 'POST',
					body: formData,  
					mode: 'cors',
					cache: 'default' };

	var dataRequest = new Request( '/directory', myInit);
      
	fetch(dataRequest)				
		.then(function(response) {
			return response.json()
		})
		.then(function(json) {		
			modalMakeDir.style.display = "none";
			showFolder(json['folders']);
			back_menu_btn.click();
			newDirForm.children.newDir_textarea.value = "";

		});

}






// Context sensual pop-up menu

var popup_menu = document.getElementById('info_popup');

var menuActive = menu.getElementsByClassName('menu');
var menu0 = menu.getElementsByClassName('menu0');
var menu1 = menu.getElementsByClassName('menu1');
var menu2 = menu.getElementsByClassName('menu2');

var back_menu_btn = document.getElementById('back');
back_menu_btn.addEventListener('click', showMenu0);

var add_menu_btn = document.getElementById('add');
add_menu_btn.addEventListener('click', showMenu1);

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


function showMenu1() {
	for (let e of menuActive) {
		e.style.display = "none";
	}
	for (let m of menu1) {
		m.style.display = "inline-block";
	}
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

