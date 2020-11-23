//	select.js

function selectModeOff() {
	
	let frames = document.getElementsByClassName('item');

	for (let frame of frames) {
		frame.removeEventListener('click', selectImages);
		frame.style.opacity='';
		let checkBox = frame.getElementsByClassName('check_box')[0];
		checkBox.style.display = 'none';
		selected = [];
		if (frame.isFile) 
			frame.addEventListener("click", bindModal);
		else {
			let href = frame.userData["folder_url"]
			frame.parentElement.setAttribute('href', href);
		};

	}

	selected = [];
}

function selectModeOn() {

	let frames = document.getElementsByClassName('item');

	for (let frame of frames) {
	
		if (frame.isFile) 
			frame.removeEventListener('click', bindModal);
		else
			frame.parentElement.removeAttribute('href');
			
		frame.addEventListener('click', selectImages);
		frame.style.opacity="0.7";
			
		
	}
			
}


function selectImages(event) {
	/*	Filling a selected array*/
	let frame = event.currentTarget;
	let checkBox = frame.getElementsByClassName('check_box')[0];
		
	if (checkBox.style.display == 'block') {
		checkBox.style.display = 'none';
				
		const index = selected.indexOf(frame);
		if (index > -1) {
			selected.splice(index, 1);
		}
				
	} else {
		checkBox.style.display ='block';
		/*	Parent's div add to a select list	*/
		selected.push(frame);
	}
		
	
};
