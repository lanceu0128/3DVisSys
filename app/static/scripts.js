function loading_screen(text) {
    $('#loading-modal').modal('show');

    var loadingTextElement = $('#loading-text') 
    loadingTextElement.text(`Loading ${text}... (0s)`);
    
    // put element update on timer
    var startTime = Date.now();
    setInterval(function () {
        var elapsedTime = Math.floor((Date.now() - startTime) / 1000);
        loadingTextElement.text(`Loading ${text}... (${elapsedTime}s)`)
    }, 500);
}

function convert_to_date(str) {
    var datePart = str.split('-')[0];
    var timePart = str.split('-')[1];
  
    var year = parseInt(datePart.substring(0, 4));
    var month = parseInt(datePart.substring(4, 6)) - 1; // subtract by 1 due to 0-based Date objects
    var day = parseInt(datePart.substring(6, 8));
    var hour = parseInt(timePart.substring(0, 2));
    
    var dateObj = new Date(year, month, day, hour);
    console.log(str, year, month, day, hour)
    
    return dateObj;
}

function convert_to_dates(date_strings) {
   return date_strings.map(convert_to_date);
}

function handle_graph_selection(button, graph) {
    graph_type = graph;

    $('.radio').removeClass('btn-primary').addClass('btn-light'); // Remove class from all buttons
    $(button).removeClass('btn-light').addClass('btn-primary'); // Add class to the clicked button
    console.log("Current graph type " + graph_type);
}

function get_graph_by_date() {
    loading_screen("page");
    graph_date = dateTimePicker.viewDate;
    form = $('#form');
    
    const year = graph_date.getFullYear();
    const month = String(graph_date.getMonth() + 1).padStart(2, "0");
    const day = String(graph_date.getDate()).padStart(2, "0");
    const hours = String(graph_date.getHours()).padStart(2, "0");
    const minutes = String(graph_date.getMinutes()).padStart(2, "0");

    const date_string = `${year}${month}${day}-${hours}${minutes}`;

    form.attr('action', `/graph/${graph_type}/${date_string}`);
    form.submit();
}

function get_latest_graph() {
    loading_screen("page");
    form = $('#form');

    form.attr('action', `/graph/${graph_type}/latest`);
    form.submit();
}