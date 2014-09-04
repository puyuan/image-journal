



$(function(){
  var group=""
  var gallery=""
  for (var i=0; i< gallery_images.length; i++){

    var item=gallery_images[i];

    // create new week 
    if(item.group!=group){
      // enable gallery
      if(gallery!=""){
        gallery.justifiedGallery({
          sizeRangeSuffixes:{'lt100':'_t', 
            'lt240':'_t', 
          'lt320':'_t', 
          'lt500':'', 
          'lt640':'_t', 
          'lt1024':'_t'}
        });

      }
      var header=$("<h3>").html(item.group)
        group=item.group

        gallery=$("<div>")
        $("#container").append(header);
      $("#container").append(gallery);

    }

    var link=$("<a>").attr({href: item.src, title:item.CreateDate, class: "swipebox"})
      var thumb=$("<img>").attr({"src": item.thumb});
    link.append(thumb);
    gallery.append(link);

  }


$(".swipebox").swipebox();

})
