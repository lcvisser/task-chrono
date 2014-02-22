function toggleDetails(elem) {
    // Get the "details"-element corresponding to the clicked element
    var e = document.getElementById(elem.id + '_details');
    
    // Toggle the visibility
    if(e.style.display == 'block') {
        e.style.display = 'none';
    } else {
        e.style.display = 'block';
    }
}
