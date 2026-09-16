var minwidth = 0;
var flgmini = false;
window.onresize = CheckLis;

jQuery(document).ready(function() {
    jQuery("#flvmenu").prepend("<div class='minmenu'><i class='fa fa-bars'></i><a>&#1052;&#1045;&#1053;&#1070;</a></div>");
    jQuery("#flvmenu > ul li ul").before("<a class='flarr'></a>");
    CheckLis();
    Setmini();
});

function CheckLis() {
    var navw;
    var allw = 0;
    var navItems;
    var wdoc = window.innerWidth;

    if (wdoc > minwidth) {
        navw = jQuery("#flvmenu").width();
        jQuery("#flvmenu").css("display", "block");
        SetAlignBl(wdoc);
        jQuery(".flarr").html("");
        if (flgmini) {
            flgmini = false;
        }
    } else {
        jQuery('#flvmenu > ul > li ul').css("height", "0").css("right", "auto").css("left", "auto");
        jQuery(".flarr").html("<i class='fa fa-plus'></i>");
        jQuery("#flvmenu").css("display", "none");
        flgmini = true;
    }
}


function Setmini() {
	jQuery(".flarr").click(function() {
		var wdoc=document.documentElement.clientWidth;
		if(minwidth > wdoc) {
			var par = this.parentElement;
			var chldul = par.getElementsByTagName('ul')[0];
			var chght = chldul.style.height; 
			if(chght == "0px") {
				jQuery(this).html("<i class='fa fa-minus'></i>");
				chldul.style.height = "auto";
			} else {
				jQuery(this).html("<i class='fa fa-plus'></i>");
				chldul.style.height = "0px";
			}
		}
	});
	jQuery(".minmenu").click(function() {
		var disp = jQuery("#flvmenu > ul").css("display");
		if(disp == "block") jQuery("#flvmenu > ul").css("display","none");
			else jQuery("#flvmenu > ul").css("display","block");
	});
}
function SetAlignBl(wdoc){
	jQuery("#flvmenu > ul > li > ul").each(
		function(){
			jQuery(this).css("left","0");
			jQuery(this).css("right","auto");
			var chldel = this.firstElementChild;
			var chlwth=0;
			if(chldel != null) chlwth = jQuery(chldel).width();
			var setel = getLeftSet(this) + chlwth;
			if(setel > wdoc) {
				jQuery(this).css("left","auto");
				jQuery(this).css("right","0");
			}
	});
	jQuery("#flvmenu > ul > li > ul > li > ul").each(
		function(){
			jQuery(this).css("left","100%");
			jQuery(this).css("right","auto");
			var chldel = this.firstElementChild;
			var chlwth=0;
			if(chldel != null) chlwth = jQuery(chldel).width();
			var setel = getLeftSet(this) + jQuery(this.parentElement).width() + chlwth;
			if(setel > wdoc) jQuery(this).css("left","-100%");
	});
}
function getLeftSet(elem) {
    var left=0;
    while(elem) {
        left = left + parseFloat(elem.offsetLeft);
        elem = elem.parentElement;
    }
	return Math.round(left);
}