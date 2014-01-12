function showLoading() {
    var d = document.getElementById("loading");
    d.style.display = "block";
}

function toggleDetails(elem) {
    var e = document.getElementById(elem.id + "_details");
    if(e.style.display == "block") {
        e.style.display = "none";
    } else {
        e.style.display = "block";
    }
}
