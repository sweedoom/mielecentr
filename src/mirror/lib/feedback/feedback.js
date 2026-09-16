$(document).ready(function(){
	
	$('.files').click(function(){
        $(this).closest('form').find('input[type=file]').click();
	});

    $('input[type=file]').change(function(){
        var form = $(this).closest('form');
    	var count = form.find("input:file")[0].files.length;
    	form.find('.files span').text('Выбрано '+count+' файл(ов)');
    });

	/* FORM EXPERT */
	
	$("#form_vopros_expert").submit(function(event){
		event.preventDefault();
		var formData = new FormData(this);
		if($('#garant_ch_expert').prop('checked')){
			$.ajax({
				url: "/lib/feedback/mail-form.php",
				type: "post",
				data: formData,
				success: function(data) {
					$("#titlepop_expert").html('<div class="thanks_form">'+data+'</div>');
				},
				error: function(){
					alert("Ваша заявка не отправлена! Попробуйте еще раз");
				},
				cache: false,
		        contentType: false,
		        processData: false
			});	
			$("#garant_error_expert").html("");
		} else {$("#garant_error_expert").html("Необходимо дать согласие");}	
	});
	
	/* FORM CONTACTS */
	
	$("#form_contacts_vopros").submit(function(event){
		event.preventDefault();
		var formData = new FormData(this);
		if($('#garant_ch_contacts').prop('checked')){
			$.ajax({
				url: "/lib/feedback/mail-form.php",
				type: "post",
				data: formData,
				success: function(data) {
					$("#titlepop_contacts").html('<div class="thanks_form">'+data+'</div>');
				},
				error: function(){
					alert("Ваша заявка не отправлена! Попробуйте еще раз");
				},
				cache: false,
		        contentType: false,
		        processData: false
			});
			$("#garant_error_contacts").html("");
		} else {$("#garant_error_contacts").html("Необходимо дать согласие");}
	});
	
	/* FORM SLIDER */
	
	$("#form_slider").submit(function(event){
		event.preventDefault();
		var formData = new FormData(this);
		if($('#garant_ch_uslugi').prop('checked')){
			$.ajax({
				url: "/lib/feedback/mail-form.php",
				type: "post",
				data: formData,
				success: function(data) {
					$(".garant").hide();
					$("#titlepop_uslugi").html('<div class="thanks_form">'+data+'</div>');
				},
				error: function(){
					alert("Ваша заявка не отправлена! Попробуйте еще раз");
				},
				cache: false,
		        contentType: false,
		        processData: false
			});
			$("#garant_error_uslugi").html("");
		} else {$("#garant_error_uslugi").html("Необходимо дать согласие");}
	});
	
	//ZAYVKA POPUP
	
	$("#form_zayvka_popup").submit(function(event){
		event.preventDefault();
		var formData = new FormData(this);
		if($('#garant_ch_zayvka').prop('checked')){
			$.ajax({
				url: "/lib/feedback/mail-form.php",
				type: "post",
				data: formData,
				success: function(data) {
					$("#titlepop_zayvka").html('<div class="thanks_form">'+data+'</div>');
					$("#form_zayvka_popup input").css("display","none");
					$("#form_zayvka_popup textarea").css("display","none");
					$("#form_zayvka_popup .button").css("display","none");
					$("#form_zayvka_popup .garant").css("display","none");
					$(".files").css("display","none");
					setTimeout(function(){
						$(".fancybox-button").click();
					},3000);
				},
				error: function(){
					alert("Ваша заявка не отправлена! Попробуйте еще раз");
				},
				cache: false,
		        contentType: false,
		        processData: false
			});		
			$("#garant_error_zayvka").html("");
		} else {$("#garant_error_zayvka").html("Необходимо дать согласие");}
	});
	
	//CALLBACK POPUP
	
	$("#form_callback_popup").submit(function(event){
		event.preventDefault();
		var formData = new FormData(this);
		if($('#garant_ch_callback').prop('checked')){
			$.ajax({
				url: "/lib/feedback/mail-form.php",
				type: "post",
				data: formData,
				success: function(data) {
					$("#titlepop_callback").html('<div class="thanks_form">'+data+'</div>');
					$("#form_callback_popup .text").css("display","none");
					$("#form_callback_popup input").css("display","none");
					$("#form_callback_popup .button").css("display","none");
					$("#form_callback_popup .garant").css("display","none");
					setTimeout(function(){
						$(".fancybox-button").click();
					},3000);
				},
				error: function(){
					alert("Ваша заявка не отправлена! Попробуйте еще раз");
				},
				cache: false,
		        contentType: false,
		        processData: false
			});
			$("#garant_error_callback").html("");
		} else {$("#garant_error_callback").html("Необходимо дать согласие");}
	});
	
	//CATALOG POPUP
	
	$("#form_catalog_popup").submit(function(event){
		event.preventDefault();
		var formData = new FormData(this);
		if($('#garant_ch_catalog').prop('checked')){
			$.ajax({
				url: "/lib/feedback/mail-form.php",
				type: "post",
				data: formData,
				success: function(data) {
					$("#titlepop_catalog").html('<div class="thanks_form">'+data+'</div>');
					$("#form_catalog_popup .text").css("display","none");
					$("#form_catalog_popup textarea").css("display","none");
					$("#form_catalog_popup input").css("display","none");
					$("#form_catalog_popup .button").css("display","none");
					$("#form_catalog_popup .garant").css("display","none");
					$("#form_catalog_popup .tovar").css("display","none");
					setTimeout(function(){
						$(".fancybox-button").click();
					},3000);
				},
				error: function(){
					alert("Ваша заявка не отправлена! Попробуйте еще раз");
				},
				cache: false,
		        contentType: false,
		        processData: false
			});
			$("#garant_error_catalog").html("");
		} else {$("#garant_error_catalog").html("Необходимо дать согласие");}
	});
	
});
