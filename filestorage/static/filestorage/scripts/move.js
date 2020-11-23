//	move.js

function exitMoveMenu() {
	$('#moveModal').hide();
	$('#moveModal-accept').off('click');
	$('#moveModal-cancel').off('click');
	$('#moveModal-back').off('click');
}


function moveFiles() {

	let dirId = $('#moveModal-accept').attr("folder-id");
	let request = getSelectedItem();

	$.ajax({
		url: '/move',
		type: 'POST',
		mode: 'same-origin',
		headers: {'X-CSRFToken': csrftoken},
		data: {
				"files": request['files'],
				"folders": request['folders'],
				"destination": dirId
			},
		
	}).done(() => {
		// TODO: Remove moved	
		selected.forEach((frame) => {
			frame.remove();
		});
	}).fail(() => {

	}).always(() => {
		back_menu_btn.click();	
	});

}



$('#move').click(moveMenu);

function moveMenu() {
	$('#moveModal').css('display', 'flex');
	$('#moveModal-accept').on('click', moveFiles)
						  .on('click', exitMoveMenu);
	$('#moveModal-cancel').click(exitMoveMenu);
	
	let backMoveMenuButton = document.getElementById('moveModal-back');
	backMoveMenuButton.parentList = [];
	backMoveMenuButton.addEventListener("click", changeParentBackButton);

	function changeParentBackButton(evnt) {
		let array = evnt.currentTarget.parentList;
		if(array.length != 0){
			let f = array.pop();
			showMoveModalContent(f['folder_id'], f['folder_name']);
		}
	}
	
	let root = $('.navbar_dir').first();
	let rootId = root.attr('folder-id');

	showMoveModalContent(rootId, "/");
	
}



function showMoveModalContent(dirId, dirName) {

	$('#moveModal-accept').attr("folder-id", dirId);
	$('#moveModal-current').text(dirName);

	let container = $('#moveModal-content');
	container.empty();

	$.ajax({
		url: '/data',
		type: 'POST',
		mode: 'same-origin',
		data: {'move_menu_folder_id': dirId},
		headers: {'X-CSRFToken': csrftoken},
		dataType: 'json',
		
	}).done(function(json) {	

		let dirs = json['folders'];
		let files = json['files'];

	
		$('<div>').addClass("moveModal-content-header")
					  	.text("Folders")
						.appendTo(container);
	
		for (let dir of dirs) {
			let d = $("<div>")
						.addClass("moveModal-item")
						.text(dir['folder_name'])
						.click(function(){
							showMoveModalContent(dir['folder_id'], dir['folder_name']);
							let backMoveMenuButton = document.getElementById('moveModal-back');
							let d = {'folder_id': dirId, 'folder_name': dirName};
							backMoveMenuButton.parentList.push(d);		

						});
		
			container.append(d);
		
		}
		
		$('<div>').addClass("moveModal-content-header")
					   .text("Files")
					   .appendTo(container)
	
		for (let file of files) {
			let d = $("<div>").addClass("moveModal-item na")
								.text(file['name']);
								
			container.append(d);
		}
		
	}).fail(() => {
		$('<div>').addClass("moveModal-content-header")
				  .text("Failure. Nothing explore.")
	  			  .appendTo(container);
	}).always(() => {
		//TODO: back button
	});


}

