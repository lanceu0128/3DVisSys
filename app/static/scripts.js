var graph_date = ""

console.log("Script loaded.")

function convert_to_date(str) {
    var datePart = str.split('_')[0]; 
    var timePart = str.split('_')[1]; 
  
    var year = parseInt(datePart.substring(0, 4));
    var month = parseInt(datePart.substring(5, 7)) - 1; // subtract by 1 due to 0-based Date objects
    var day = parseInt(datePart.substring(8, 10));
    var hour = parseInt(timePart);

    var dateObj = new Date(year, month, day, hour);
    
    console.log(dateObj)
    return dateObj
}

function convert_to_dates(date_strings) {
   return date_strings.map(convert_to_date)
}

function handle_graph_selection(button, graph) {
    graph_type = graph

    $('.nav-item button').removeClass('bg-danger');
    $('.nav-item button').addClass('bg-primary');
    button.classList.add("bg-danger");
    console.log("Current graph type " + graph_type)
}

function get_graph_by_date() {
    graph_date = dateTimePicker.viewDate
    
    const year = graph_date.getFullYear();
    const month = String(graph_date.getMonth() + 1).padStart(2, "0");
    const day = String(graph_date.getDate()).padStart(2, "0");
    const hours = String(graph_date.getHours()).padStart(2, "0");
    const minutes = String(graph_date.getMinutes()).padStart(2, "0");

    const dateString = `${year}-${month}-${day}_${hours}-${minutes}`;

    url = "/graph_by_date/" + dateString

    $.ajax({
        type : "POST",
        url : url,
        contentType: 'application/json',
        success: function (response) {
            console.log("POST response received from " + url)
            $('#body').html(response.rendered_template);
        }
    });
}

function get_latest_graph() {
    url = "/graph_latest"

    $.ajax({
        type : "POST",
        url : url,
        contentType: 'application/json',
        success: function (response) {
            console.log("POST response received from " + url)
            $('#body').html(response.rendered_template);
        }
    });
}