function toggleDetails(elem) {
    // Get the "details"-table corresponding to the clicked element
    var e = document.getElementById(elem.id + '_details');
    
    // Toggle the visibility
    if(e.style.display == 'block') {
        e.style.display = 'none';
    } else {
        e.style.display = 'block';
    }
}

function setEventHandlers() {
    // Define labels
    var name_label = 'Task name';
    var estimate_label = 'Estimated duration (e.g. 1d 5h 30m)';
    
    // Define colors
    var active_color = '#000000';
    var inactive_color = '#cbcbcb';
    
    // Set properties of the "name"-input field
    var name_field = document.getElementById('name_field');
    name_field.value = name_label;
    name_field.style.color = inactive_color;
    name_field.onfocus = function() {
            handleFocusEvent(name_field, name_label, active_color);
        };
    
    // Properties of the "duration"-input field
    var estimate_field = document.getElementById('estimate_field');
    estimate_field.value = estimate_label;
    estimate_field.style.color = inactive_color;
    estimate_field.onfocus = function() {
            handleFocusEvent(estimate_field, estimate_label, active_color);
        };
}

function handleFocusEvent(elem, label, color) {
    // Clear field if description is still shown
    if (elem.value == label) {
        elem.value = '';
    }
    
    // Change color
    elem.style.color = color;
}

function updateTimers() {
    // Get all tasks that are labeled in progress
    var tasks = document.getElementsByClassName('task in_progress');
    if (tasks.length > 0) {
        // Update timers for each task that is in progress
        for (var i = 0; i < tasks.length; i++) {
            // Get current time
            var elem = tasks[i].getElementsByClassName('duration');
            var s = elem[0].innerHTML.split(':');
            var hours = parseInt(s[0], 10);
            var mins = parseInt(s[1]);
            var secs = parseInt(s[2]);
            
            // Update seconds
            secs += 1;
            if (secs >= 60) {
                secs -= 60;
                mins += 1;
            }
            
            // Update hours
            if (mins >= 60) {
                mins -= 60;
                hours += 1;
            }
            
            // Convert hours to string representation
            var hours_str = hours.toString();

            // Convert minutes to string representation            
            var mins_str = '';            
            if (mins < 10) {
                mins_str = '0';
            }
            mins_str += mins.toString();

            // Convert seconds to string representation
            var secs_str = '';            
            if (secs < 10) {
                secs_str = '0';
            }
            secs_str += secs.toString();
            
            // Update element
            elem[0].innerHTML = hours_str + ':' + mins_str + ':' + secs_str;
        }
    }
}

function listSetup() {
    // Set up event handlers for input field
    setEventHandlers();
    
    // Set callback for updating the timers
    setInterval(updateTimers, 1000);
}
