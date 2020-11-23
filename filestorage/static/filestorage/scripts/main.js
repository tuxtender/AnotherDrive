//	main.js

let gallery = document.getElementById('gallery');
let menu = document.getElementById('menu');

var csrftoken = getCookie('csrftoken');
let selected = [];

getUserData();
resizeGalleryWallpaper();

function getUserData() {

	jQuery.ajax({
		url: '/data',
		type: 'POST',
		mode: 'same-origin',
		headers: {'X-CSRFToken': csrftoken},
		dataType: 'json',
	}).then(function(json) {
		showFolder(json['folders'])		
		showImage(json['files']);	
		resizeGalleryWallpaper();

	});
}

/*	Create new a document element for manipulations files server	*/
/*	(view, order, save, load)  										*/

function showImage(data) {
	for (let pic of data) {
		let div = document.createElement('div');
		div.isFile = true;
		div.userData = pic; //Put server data of each element to div.frame
		div.modalImgUrl;	//Undefined image for Modal
		div.setAttribute('class', 'item pic responsive thumbnail');
		div.setAttribute('file-id', pic['file_id']);
		div.setAttribute('file-name', pic['name']);
		/*	A thumbnail image of div's container	*/
	
		let img = document.createElement('img');
		//img.src = pic['thumb'];
		img.alt = pic['name'];
		img.setAttribute('class', 'image');

		$.ajax({
			url: '/source' + "?t=" +  pic['file_id'],
			type: 'GET',
			mode: 'same-origin',
			xhrFields: {
				responseType: 'blob'
			},
			
		}).done((image) => {
			img.src = URL.createObjectURL(image);
			
		}).fail(function() {
			img.src = "/static/filestorage/images/na.jpg";
		});

		/*	Create a check box on image*/
		let checkBox = document.createElement('div');
		checkBox.setAttribute('class', 'check_box');

		let checker = document.createElement('img');
		checker.setAttribute('class', 'checker');
		checker.src = "/static/filestorage/images/accept.svg";

		checkBox.appendChild(checker);

		let name = document.createElement('div');
		name.setAttribute('id', 'file_name');
		name.setAttribute('class', 'frame_name');
		name.innerText = pic['name'];

		/*	Info about sharing	*/
		let share = document.createElement('img');
		share.setAttribute('class', 'share-status filter-green');
		share.src = "/static/filestorage/images/share_file.svg";
		if (pic['is_share']) {
			share.style.display = "block";
		} else {
			share.style.display = "none";
		}

	

		div.appendChild(img);
		div.appendChild(checkBox);
		div.appendChild(share);
		div.appendChild(name);

		gallery.appendChild(div);

		div.addEventListener('click', bindModal);
	}
};


function showFolder(data) {
	
	for (let dir of data) {
		let a = document.createElement('a');
		//a.setAttribute('class', "directory");
		//a.setAttribute('class', "item");
		a.setAttribute('href', dir['folder_url']);
		a.setAttribute('folder-id', dir['folder_id'])

		let div = document.createElement('div');
		div.userData = dir; //Put server data of each element to div.frame

		div.setAttribute('class', 'item directory responsive thumbnail');
			
		
		let img = document.createElement('img');
		img.src = '/static/filestorage/images/folder.png';
		img.alt = dir['folder_name'];
		img.setAttribute('class', 'image ');
		
		
		let checkBox = document.createElement('div');
		checkBox.setAttribute('class', 'check_box');
		
		let checker = document.createElement('img');
		checker.setAttribute('class', 'checker');
		checker.src = "/static/filestorage/images/accept.svg";

		checkBox.appendChild(checker);

		/*	Info about sharing	*/
		let share = document.createElement('img');
		share.setAttribute('class', 'share-status filter-green');
		share.src = "/static/filestorage/images/share_file.svg";
		if (dir['is_share']) {
			share.style.display = "block";
		} else {
			share.style.display = "none";
		}			

		let name = document.createElement('div');
		name.setAttribute('class', 'frame_name');
		name.innerText = dir['folder_name'];
		
		a.appendChild(div);
		div.appendChild(img);
		div.appendChild(checkBox);
		div.appendChild(share);
		div.appendChild(name);
		gallery.appendChild(a);
		
		
	
	}

};



window.addEventListener("resize", resizeGalleryWallpaper);

function resizeGalleryWallpaper() {
	let y = gallery.getBoundingClientRect()["top"];
	let maxY = window.innerHeight;
	let minHeight = maxY - (Number(y)).toFixed() ;
	gallery.style.minHeight = minHeight +"px";
}


function getCurrentDirectory() {
	var navBar = document.getElementById('nav_bar');
	let link = navBar.lastElementChild.getAttribute("href");

	let l = link.split("/")
	let dirId = l[l.length-1]
	return dirId
}


function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function getSelectedItem(){

	let data = {};
	let files = [];
	let folders = [];

	for (let frame of selected) {
		if (frame.isFile) 
			files[files.length] = frame.userData['file_id'];
		else 
			folders[folders.length] = frame.userData['folder_id'];
	}

	data['files'] = JSON.stringify(files);
	data['folders'] = JSON.stringify(folders);

	

	return data
}
