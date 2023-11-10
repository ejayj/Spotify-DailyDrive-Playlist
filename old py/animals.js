// JavaScript code

//let button = document.getElementById("ply"); //how to display the name of what was clicked?
//button.addEventListener("click", winal());


function search_animal() {
    let input = document.getElementById('searchbar').value
    input=input.toLowerCase(); //I may want to get rid of this for my case sensitive playlists
    let x = document.getElementsByClassName('animals');  //this is where it gets all of the elements to search for, i can replace this with playlists
      
    for (i = 0; i < x.length; i++) {  //the loop that displays the text
        if (!x[i].innerHTML.toLowerCase().includes(input)) {
            x[i].style.display="none";
        }
        else {
            x[i].style.display="list-item";                 
        }
    }
}



function zoom() {
    //var id = ele.id;

    window.alert('area element id = ');// + id);
    let passed = 'passy';
    okay(passed);
}

function okay(passed) {
    window.alert(passed);
}

function winal() {
    window.alert('hi');
}

function winall2(message) {
    window.alert(message);
}