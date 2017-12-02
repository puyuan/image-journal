function checkVisible() {
  var galleries = $(".galleria:in-viewport");
  var gallery;
  for (var i = 0; i < galleries.length; i++) {
    gallery = $(galleries[i]);
    if (!gallery.hasClass("justified-gallery")) {
      createGallery(gallery);
      break;
    }
  }
}

function createGallery(gallery) {
  var group = gallery.attr("id");

  if (gallery.hasClass("justified-gallery"))
    return;

  console.log("creating gallery", group);

  var images = gallery.find("img");

  for (var i = 0; i < images.length; i++) {
    var image = $(images[i]);
    var image_src = image.attr("safe-src");
    image.attr({ src: image_src });
  }

  gallery.justifiedGallery({
    sizeRangeSuffixes: {
      'lt100': '_t',
      'lt240': '_t',
      'lt320': '_t',
      'lt500': '',
      'lt640': '_t',
      'lt1024': '_t'
    },
    rowHeight: "300px"
  }).on('jg.complete', function (e) {
    checkVisible();
  });
}

journalData = {};
function loadjournal(){
  fetch('/api/journal')
    .then(
    function (response) {
      if (response.status !== 200) {
        console.log('Looks like there was a problem. Status Code: ' +
          response.status);
        return;
      }

      // Examine the text in the response
      response.json().then(function (data) {

        for (var i = 0; i < data.entries.length; i++) {
          var entry = data.entries[i];
          var timestamp = entry.date + "T" + entry.time
          journalData[timestamp] = entry;
        }
        loadGallery();


      });

    }
    )
    .catch(function (err) {
      console.log('Fetch Error :-S', err);
    });

}



$(function () {
  loadjournal();
})

function loadGallery() {
  fetch("/api/gallery/images", {
    method: 'get'
  }).then(function(response){
      response.json().then(function(data){

          renderGallery(data.images);
      })

  })
}

function renderGallery(gallery_images) {

  var group = ""
  var gallery = ""
  for (var i = 0; i < gallery_images.length; i++) {

    var item = gallery_images[i];

    // create new week
    if (item.group != group) {
      var header = $("<h3>").html(item.group);
      group = item.group;

      gallery = $("<div>").attr({ id: item.group, class: "galleria" });
      $("#container").append(header);
      $("#container").append(gallery);

    }

    // add thumbnails to gallery, but don't initialize it yet.
    //var link=$("<a>").attr({href: item.src, title:item.CreateDate, class: "swipebox"});
    var thumb = addThumbEvent(item)
    //link.append(thumb);
    gallery.append(thumb);

  }

  //$(".swipebox").swipebox();
  checkVisible();

  var submitButton = document.getElementById("submit");
  submitButton.addEventListener("click", function () {
    var journal = document.getElementById("journal");
    var item = JSON.parse(journal.dataset.item);
    var content = document.getElementById("journal_entry").value;

    fetch("/journal", {
      method: 'post',
      headers: {
        "Content-type": "application/x-www-form-urlencoded; charset=UTF-8"
      },
      body: 'timestamp= ' + item["CreateDate"] + '&content=' + content
    });

  });


}

function addThumbEvent(item) {
  var thumb = $("<img>").attr({ "safe-src": item.thumb });

  item.content = journalData[item["CreateDate"].substring(0, 16)]
  if (item.content) {
    thumb.addClass("glow");
  }
  console.log(journalData[item["CreateDate"].substring(0, 16)], item["CreateDate"].substring(0, 16))


  thumb[0].addEventListener("click", function () {
    console.log(item)
    var journal_title = document.getElementById("journal_title");
    var journal = document.getElementById("journal");
    var journal_entry = document.getElementById("journal_entry");

    journal_title.innerHTML = item["CreateDate"]
    if (item.content) {
      journal_entry.value = item.content.title + " " + item.content.body;
    }

    else
      journal_entry.value = "";
    journal.showModal();
    journal.dataset.item = JSON.stringify(item);
  });




  return thumb;
}

$(window).scroll(checkVisible)