function toggleDetails(elem) {
    var e = document.getElementById(elem.id + '_details');
    if(e.style.display == 'block') {
        e.style.display = 'none';
    } else {
        e.style.display = 'block';
    }
}

function setEventHandlers() {
    var active_color = '#000000';
    var inactive_color = '#cbcbcb';
    
    var name_label = 'Task name';
    var name_field = document.getElementById('name_field');
    
    var estimate_label = 'Estimated duration (e.g. 1d 5h 30m)';
    var estimate_field = document.getElementById('estimate_field');
    
    name_field.value = name_label;
    name_field.style.color = inactive_color;
    name_field.onfocus = function() { handleFocusEvent(name_field, name_label, active_color); };
    
    estimate_field.value = estimate_label;
    estimate_field.style.color = inactive_color;
    estimate_field.onfocus = function() { handleFocusEvent(estimate_field, estimate_label, active_color); };
}

function handleFocusEvent(elem, label, color) {
    if (elem.value == label) {
        elem.value = '';
    }
        elem.style.color = color;
}
