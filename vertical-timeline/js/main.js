
function createTimeline(){

  var timelineBlock=$("<div>").attr({class: "cd-timeline-block"});
  var timelineicon=$("<div>").attr({"class": "cd-timeline-img cd-picture"})
  timelineicon.html('<img src="img/cd-icon-picture.svg" alt="Picture">')
  var timelineContent=$("<div>").attr({"class": "cd-timeline-content" })
  timelineBlock.append(timelineicon)
  timelineBlock.append(timelineContent)
  return timelineBlock
}


jQuery(document).ready(function($){

  var timelineBlock=null;
  var date=null
	 for (var i=0; i< gallery_images.length; i++){

    var item=gallery_images[i];
    var timelineContent;

    // create new week 
    if(item.date!=date){
    // enable gallery
  
      if (timelineBlock)
        $("#cd-timeline").append(timelineBlock);        
      timelineBlock=createTimeline();
      date=item.date
      timelineContent=timelineBlock.find(".cd-timeline-content");
      timelineContent.html("<span class='cd-date'>"+date+"</span><div class='photoset-grid' data-layout='1221'></div> ");
        

      }

      timelineContent=timelineBlock.find(".photoset-grid");
      timelineContent.append($("<img>").attr({src:"../"+ item.thumb}))

      }

        $(".photoset-grid").photosetGrid({width: "250px"});


        var $timeline_block = $('.cd-timeline-block');

	//hide timeline blocks which are outside the viewport
	$timeline_block.each(function(){
		if($(this).offset().top > $(window).scrollTop()+$(window).height()*0.75) {
			$(this).find('.cd-timeline-img, .cd-timeline-content').addClass('is-hidden');
		}
	});

	//on scolling, show/animate timeline blocks when enter the viewport
	$(window).on('scroll', function(){
		$timeline_block.each(function(){
			if( $(this).offset().top <= $(window).scrollTop()+$(window).height()*0.75 && $(this).find('.cd-timeline-img').hasClass('is-hidden') ) {
				$(this).find('.cd-timeline-img, .cd-timeline-content').removeClass('is-hidden').addClass('bounce-in');
			}
		});
	});
});
