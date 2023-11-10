var redirect_uri = "http://127.0.0.1:5500/index.html";
var CLIENT_ID="1f69a9d216f6424f92fb177324f1e06c"
var CLIENT_SECRET="6049a8ed4fc9431b92cd0476b6ba039a"

const AUTHORIZE = "https://accounts.spotify.com/authorize";

function OnPageLoad(){
    if ( window.location.search.length > 0){
        handleRedirect();
    }
}

function handleRedirect(){
    let code = getCode();
    console.log(code); // use cmd option C to open log in safari
}

function getCode(){
    let code = null;
    const queryString = window.location.search;
    if ( queryString.length > 0) {
        const urlParams = new URLSearchParams(queryString);
        code = urlParams.get('code')
    }
    return code;
}

function RA(){
    //client_id = document.getElementById("clientId").value;
    //client_secret = document.getElementById("clientSecret").value;

    // auth_string = client_id + ":" + client_secret
    // auth_bytes = auth_string.encode("utf-8")
    // auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    
    // url = "https://accounts.spotify.com/api/token"

    // headers = {
    //     "Authorization": "Basic " + auth_base64,
    //     "Content-Type": "application/x-www-form-urlencoded"
    // }

    let url = AUTHORIZE;
    url += "?client_id=" + CLIENT_ID;
    url += "&response_type=code";
    url += "&show_dialog=true";
    url += "&scope=playlist-modify-public";
    url += "&redirect_uri=http://127.0.0.1:5500/index.html"
    window.location.href = url; //show spotify's auth screen
}
