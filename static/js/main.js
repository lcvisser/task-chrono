function toggleDetails(elem) {
    // Get the "details"-element corresponding to the clicked element
    var e = document.getElementById(elem.id + '_details');
    
    // Toggle the visibility
    if (e.style.display == 'block') {
        e.style.display = 'none';
    } else {
        e.style.display = 'block';
    }
}

function hlDelete() {
    // Get the "delete" form element
    var e = document.getElementById('delete_tasks_field');
    
    // Toggle highlight
    if (e.className.indexOf('warning') == -1) {
        e.className += ' warning';
    } else {
        e.className = e.className.replace('warning', '');
    }
}
