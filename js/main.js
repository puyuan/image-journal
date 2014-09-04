function checkVisible(){

  var galleries=$(".galleria:in-viewport");

  var gallery;
  for (var i=0; i< galleries.length; i++){
    gallery=$(galleries[i]);
    if(!gallery.hasClass("justified-gallery")){
      createGallery(gallery);
      break;
    }
  }




}
function createGallery(gallery){
  var group=gallery.attr("id");

  if(gallery.hasClass("justified-gallery"))
    return;

  console.log("creating gallery", group);

  var images=gallery.find("img");


  for (var i=0; i< images.length; i++){
    var image=$(images[i]);
    var image_src=image.attr("safe-src");
    image.attr({src: image_src});
  }

  gallery.justifiedGallery({
    sizeRangeSuffixes:{'lt100':'_t', 
      'lt240':'_t', 
    'lt320':'_t', 
    'lt500':'', 
    'lt640':'_t', 
    'lt1024':'_t'} 
  }).on('jg.complete', function(e){
    checkVisible();


  });
}



$(function(){
  var group=""
  var gallery=""
  for (var i=0; i< gallery_images.length; i++){

    var item=gallery_images[i];

    // create new week 
    if(item.group!=group){
      var header=$("<h3>").html(item.group);
      group=item.group;

      gallery=$("<div>").attr({id: item.group, class: "galleria"});
      $("#container").append(header);
      $("#container").append(gallery);

    }

    // add thumbnails to gallery, but don't initialize it yet. 
    var link=$("<a>").attr({href: item.src, title:item.CreateDate, class: "swipebox"});
    var thumb=$("<img>").attr({"safe-src": item.thumb});
    link.append(thumb);
    gallery.append(link);


  }

$(".swipebox").swipebox();
checkVisible();



})

$(window).scroll(checkVisible)


