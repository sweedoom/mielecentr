$(document).ready(function(){

	$(".mygallery").justifiedGallery({
		rowHeight : 130,
		lastRow : 'nojustify',
		captions : false,
		border : 0,
		margins : 7
	});
	$(".mygallery-catalog").justifiedGallery({
		rowHeight : 60,
		lastRow : 'nojustify',
		captions : false,
		border : 0,
		margins : 7
	});
	
	//Slider main page
	$(".owl-carousel").owlCarousel({
		items:1,
		loop:true,
		margin:0,
		nav:true,
		autoplay:true,
		autoplayTimeout:6000,
		smartSpeed:750,
		autoplayHoverPause:false
	});
	$(".owl-prev").html("<i class='fa fa-angle-left'></i>");
	$(".owl-next").html("<i class='fa fa-angle-right'></i>");
	
	// Stiky menu - sidebar
	$('#sidebar_fixed').sticky({topSpacing:70});

	//Slider Index v.1.6.0	- sidebar photo
	$("#index_photo").slick({
		arrows: true,
		nextArrow: '<i class="fa fa-arrow-circle-right nextarr" aria-hidden="true"></i>',
		prevArrow: '<i class="fa fa-arrow-circle-left prevarr" aria-hidden="true"></i>',
		dots: false,
		infinite: true,
		speed: 300,
		slidesToShow: 4,
		slidesToScroll: 4,
		responsive: [
			{
				breakpoint: 1024,
				settings: {
					slidesToShow: 3,
					slidesToScroll: 3,
					infinite: true,
					dots: false
				}
			},
			{
				breakpoint: 768,
				settings: {
					slidesToShow: 2,
					slidesToScroll: 2
				}
			},
			{
				breakpoint: 480,
				settings: {
					slidesToShow: 1,
					slidesToScroll: 1
				}
			}
		]
	});

	//Slider Index v.1.6.0	- partnery
	$("#index_partnery").slick({
		arrows: true,
		nextArrow: '<i class="fa fa-arrow-circle-right nextarr" aria-hidden="true"></i>',
		prevArrow: '<i class="fa fa-arrow-circle-left prevarr" aria-hidden="true"></i>',
		dots: false,
		infinite: true,
		autoplay: true,
		autoplaySpeed: 2000,
		speed: 300,
		slidesToShow: 5,
		slidesToScroll: 1,
		responsive: [
			{
				breakpoint: 1024,
				settings: {
					slidesToShow: 5,
					slidesToScroll: 1,
					infinite: true,
					dots: false
				}
			},
			{
				breakpoint: 992,
				settings: {
					slidesToShow: 4,
					slidesToScroll: 1,
					infinite: true,
					dots: false
				}
			},
			{
				breakpoint: 768,
				settings: {
					slidesToShow: 3,
					slidesToScroll: 1
				}
			},
			{
				breakpoint: 480,
				settings: {
					slidesToShow: 2,
					slidesToScroll: 1
				}
			}
		]
	});
	
	//Slider Slick v.1.6.0	- sidebar photo
	$("#sidebar_photo").slick({
		arrows: true,
		nextArrow: '<i class="fa fa-arrow-circle-right nextarr" aria-hidden="true"></i>',
		prevArrow: '<i class="fa fa-arrow-circle-left prevarr" aria-hidden="true"></i>',
		infinite: true,
		speed: 500
	});
	
	//Slider Slick v.1.6.0	- sidebar otzyv
	$("#sidebar_otzyv").slick({
		arrows: true,
		nextArrow: '<i class="fa fa-arrow-circle-right nextarr" aria-hidden="true"></i>',
		prevArrow: '<i class="fa fa-arrow-circle-left prevarr" aria-hidden="true"></i>',
		infinite: true,
		speed: 500
	});

	//Slider Slick v.1.6.0	- sidebar action
	$("#sidebar_action").slick({
		arrows: true,
		nextArrow: '<i class="fa fa-arrow-circle-right nextarr" aria-hidden="true"></i>',
		prevArrow: '<i class="fa fa-arrow-circle-left prevarr" aria-hidden="true"></i>',
		autoplay: true,
		autoplaySpeed: 4000,
		infinite: true,
		speed: 500
	});
	
	//Slider Slick v.1.6.0	- uslugi bottom
	$('#carousel_photo').slick({
		arrows: true,
		nextArrow: '<i class="fa fa-arrow-circle-right nextarr" aria-hidden="true"></i>',
		prevArrow: '<i class="fa fa-arrow-circle-left prevarr" aria-hidden="true"></i>',
		dots: false,
		infinite: true,
		speed: 300,
		slidesToShow: 3,
		slidesToScroll: 3,
		responsive: [
			{
				breakpoint: 1024,
				settings: {
					slidesToShow: 3,
					slidesToScroll: 3,
					infinite: true,
					dots: false
				}
			},
			{
				breakpoint: 768,
				settings: {
					slidesToShow: 2,
					slidesToScroll: 2
				}
			},
			{
				breakpoint: 480,
				settings: {
					slidesToShow: 1,
					slidesToScroll: 1
				}
			}
		]
	});
	
	// Taby - calc
	$("#tabs").lightTabs();
	
	//Maska nomer phone
	//$(".inputmask").inputmask("+7 (999) 999-99-99");
	$('.inputmask').inputmask("mask", {
		 "mask": "+7(*99) 999-99-99",
		 "clearIncomplete": true,
		 "showMaskOnHover": true,
		 "showMaskOnFocus": false,
		 "definitions": { '*': { "validator": "[0-69]" }}
	});
	// Spaces in a prices
	$(".pricespace").each(function(){
		var price = $(this).html();
		var parts = (price + '').split('.');
        var main = parts[0];
        var len = main.length;
        var pricetxt = '';
        var i = len - 1;
		while(i >= 0) {
			pricetxt = main.charAt(i) + pricetxt;
			if ((len - i) % 3 === 0 && i > 0) {
				pricetxt = ' ' + pricetxt;
			}
			--i;
		}
		if (parts.length > 1) { pricetxt += '.' + parts[1]; }
		$(this).html(pricetxt);
	});

});		