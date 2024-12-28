var CLIENT_ID="1f69a9d216f6424f92fb177324f1e06c";
var CLIENT_SECRET="6049a8ed4fc9431b92cd0476b6ba039a";
var code="";
const AUTHORIZE = "https://accounts.spotify.com/authorize";
var redirect_uri = 'http://127.0.0.1:5000/'; // example value from spotify: http://localhost:8888/callback -> this value needs to be allowed on spotify's end in dev settings

function RA(){
    let url = AUTHORIZE;
    url += "?client_id=" + CLIENT_ID;
    url += "&response_type=code";
    //url += "&show_dialog=true"; //force user to login again?
    //url += "&state=xyz" //i should add some adqeuate code here
    url += "&scope=playlist-read-private playlist-modify-public playlist-modify-private ugc-image-upload user-read-private";
    url += "&redirect_uri=" + redirect_uri;
    window.location.href = url; //show spotify's auth screen
}

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


document.addEventListener('DOMContentLoaded', () => {
    // Functions to open and close a modal
    function openModal($el) {
      $el.classList.add('is-active');
    }
  
    function closeModal($el) {
      $el.classList.remove('is-active');
    }
  
    function closeAllModals() {
      (document.querySelectorAll('.modal') || []).forEach(($modal) => {
        closeModal($modal);
      });
    }
  
    // Add a click event on buttons to open a specific modal
    (document.querySelectorAll('.js-modal-trigger') || []).forEach(($trigger) => {
      const modal = $trigger.dataset.target;
      const $target = document.getElementById(modal);
  
      $trigger.addEventListener('click', () => {
        openModal($target);
      });
    });
  
    // Add a click event on various child elements to close the parent modal
    (document.querySelectorAll('.modal-background, .modal-close, .modal-card-head .delete, .modal-card-foot .button') || []).forEach(($close) => {
      const $target = $close.closest('.modal');
  
      $close.addEventListener('click', () => {
        closeModal($target);
      });
    });
  
    // Add a keyboard event to close all modals
    document.addEventListener('keydown', (event) => {
      if (event.code === 'Escape') {
        closeAllModals();
      }
    });
  });