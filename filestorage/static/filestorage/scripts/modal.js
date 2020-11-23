//	modal.js

/*	Modal image viewer and posting comments	*/

const modal = document.getElementById('modal-view');

function bindModal(evnt) {
	
	$(modal).css('display', 'flex');
	$(gallery).css('filter', 'blur(4px)');

		
	$('#download_modal').off('click');
    $('#modal-next').off('click');
    $('#modal-prev').off('click');
    $('#modal-close').off('click');
	
	let	pics = document.getElementsByClassName('pic');	

	let list = [];
	for (let e of pics) {
		list.push(e);
	}
	
	let frame = evnt.currentTarget;
	let i = list.indexOf(frame);
		
	setImage(frame);
	getComments();
	
	$('#download_modal').off('click');
	$('#download_modal').click( function() {
		downloadFile();
	});

	$('#modal-next').click( function() {
		i += 1;
		if (i >  pics.length - 1)
			i = 0;
		
		setImage(pics[i]);
		getComments();
	});

	$('#modal-prev').click( function() {
		i -= 1;
		if (i < 0)
			i = pics.length - 1 ;
		
		setImage(pics[i]);
		getComments();
	});	

	// When the user clicks on <span> (x), close the modal
	$('#modal-close').click( function() { 
		$(modal).css('display', 'none');
		$(gallery).css('filter', '');
	});

};


function setImage(frame) {
	let fileId = frame.userData['file_id'];
	let name = frame.userData['name'];
	let modal = $('#modal-view');
	let modal_image = $('#modal_image');
	modal.attr('file-id', fileId);
	modal.attr('file-name', name);
		
	if(frame.modalImgUrl == null) {
		
		$.ajax({
			url: '/source?m=' + fileId,
			type: 'GET',
			headers: {'X-CSRFToken': csrftoken},
			xhrFields: {
				responseType: 'blob' // to avoid binary data being mangled on charset conversion
			},
		
		  }).done(function(blob) {
				frame.modalImgUrl = URL.createObjectURL(blob);
				modal_image.attr('src', frame.modalImgUrl);
		  }).fail(function() {
				modal_image.attr('src', "/static/filestorage/images/na.jpg");	
		  }).always(() => {
			
		});


	} else {
		modal_image.attr('src', frame.modalImgUrl);		
	}
}




function downloadFile() {
	let fileId = $('#modal-view').attr('file-id');
	let originalName = $('#modal-view').attr('file-name');
	
	const fileRequest = new Request('/source?i=' + fileId, {
		method: 'GET',
		mode: 'cors',
		cache: 'default',
	});

	fetch(fileRequest)
		.then((response) => response.blob())
		.then((file) => {
			
			let link = document.createElement("a");
			link.style.display = 'none';
			document.body.appendChild(link);
			link.href = URL.createObjectURL(file);
			link.download = originalName;
			link.click();
			//	Free memory after a few minutes
			setTimeout(function() {
				URL.revokeObjectURL(link.href);
				link.remove(); 
			}, 6000);
				
	  });
		
}


var commentForm = document.getElementById('commentForm');
commentForm.addEventListener('submit', sendComment);


function sendComment(evnt) {

	evnt.preventDefault();
	let fileId = $('#modal-view').attr('file-id');
	
	let formData = new FormData(commentForm);
	formData.append('file_id', fileId); 
		
	const modalCommentsRequest = new Request('/comment', {
		method: 'POST',
		body: formData,
		mode: 'same-origin',  
		cache: 'default'
	});

	fetch(modalCommentsRequest)
		.then((response) => response.json())
		.then(() => {
			getComments();
			$("#commentForm").trigger("reset");
	  });

}

function getComments() {

	let fileId = $('#modal-view').attr('file-id');

	/*	Clear */
	$('#comments').empty();
	
	let formData = new FormData();
	formData.append('file_id', fileId); 
	
	const modalCommentsRequest = new Request('/comment', {
		method: 'POST',
		body: formData,
		mode: 'same-origin',
		headers: {'X-CSRFToken': csrftoken} 
	});

	fetch(modalCommentsRequest)
		.then((response) => response.json())
		.then((records) => {
			
			for (let rec of records['comments']) {
			
				let user = document.createElement('span');
				user.innerText = rec['author'];
				user.setAttribute('class', 'modal_comment_author');
				
				let date = document.createElement('span');
				date.innerText = rec['date'];
				date.setAttribute('class', 'modal_comment_date');
				
				let text = document.createElement('div');
				text.innerText = rec['text'];
				text.setAttribute('class', 'modal_comment_text');
				
				let c = document.createElement('div');
				c.appendChild(user);
				c.appendChild(date);
				c.appendChild(text);
	
				$('#comments').append(c);
			
			}
			
	  });

}

