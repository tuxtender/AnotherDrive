//	remove.js

$('#delete').click(delFiles);

function delFiles() {

	let request = getSelectedItem();
	
	$.ajax({
		url: '/remove',
		type: 'POST',
		mode: 'same-origin',
		headers: {'X-CSRFToken': csrftoken},
		data: {
			"files": request['files'],
			"folders": request['folders']
		},
		
	}).done(() => {
		//TODO: Remove selected from gallery
		selected.forEach((frame) => {
			frame.remove();
		});
	}).always(() => {
		$('#back').trigger('click');
	});
}

