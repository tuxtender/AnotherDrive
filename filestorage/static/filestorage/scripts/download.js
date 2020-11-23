//	download.js

$('#download').click(downloadZip);

function downloadZip() {
		
	let request = getSelectedItem();
	
	console.log(request['files']);

	console.log(request['folders']);

	$.ajax({
		url: '/download',
		type: 'POST',
		mode: 'same-origin',
		headers: {'X-CSRFToken': csrftoken},
		xhrFields: {
			responseType: 'blob'
		},
		data: {
				"files": request['files'],
				"folders": request['folders']
		},
		
	}).done((zipArchive) => {
		window.location.href = URL.createObjectURL(zipArchive);
	}).always(() => {
		back_menu_btn.click();	

	});
	


}

