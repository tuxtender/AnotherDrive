//	share.js



$('#share').click(() => {
	$('#share_modal').css('display', 'flex');

});

$('#shareModal-cancel').click(() =>{
	$('#share_modal').css('display', 'none');
	$('#back').trigger('click');
});


$('#shareModal-accept').click(share);

function share() {

	let selectedValue = document.getElementById("shareModal-select").value;
	request = getSelectedItem();
	
	$.ajax({
		url: '/share',
		type: 'POST',
		mode: 'same-origin',
		headers: {'X-CSRFToken': csrftoken},
		data: {
			"files": request['files'],
			"folders": request['folders'],
			'share_mode': selectedValue
		},
		dataType: 'json',
		
	}).done((json) => {
		if (json['share_link']){
			alert(json['share_link']);
		}
			selected.forEach((frame) => {
				frame.remove();
			});

			showFolder(json['items']['folders']);	
			showImage(json['items']['files']);	

		
		
	}).always(() => {
		$('#share_modal').css('display', 'none');
		back_menu_btn.click();
	});
	
}



