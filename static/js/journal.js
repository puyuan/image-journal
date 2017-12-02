function loadJournal() {

    fetch('/api/journal/combined').then(
        function (response) {
            if (response.status !== 200) {
                console.log('Looks like there was a problem. Status Code: ' + response.status);
                return;
            }
            // Examine the text in the response
            response.json().then(function (data) {
               renderJournal(data.entries);
            });

        });

}


function renderJournal(entries) {

    var contentDiv = document.getElementById("content");

    for (var i = 0; i < entries.length; i++) {

        contentDiv.innerHTML += "<div class='clear'>\n<h3 class='uppercase float-left'>" + entries[i].title + "</h3>"
        contentDiv.innerHTML += "<span class='float-right'>"
            + entries[i].date + " " + entries[i].time + "</span>\n</div><hr class='clear'>"


        contentDiv.innerHTML += '<img class="float-left" width=300 src="' + entries[i].url + '">';

        var p_arr = entries[i].body.split("\n");
        for (var j = 0; j < p_arr.length; j++)
            contentDiv.innerHTML += "<p>" + p_arr[j] + "</p>"


    }


}


loadJournal();
