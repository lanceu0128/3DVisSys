var graph_type = "3Drefl"

console.log("Script loaded.")

function loading_screen() {
    $('#loading-modal').modal('show');

    var startTime = Date.now();
    var loadingTextElement = $('#loading-text');
    loadingTextElement.text('Loading... (0s)');

    // Update the loading text every 500 milliseconds (adjust as needed)
    setInterval(function () {
        // Calculate elapsed time
        var elapsedTime = Math.floor((Date.now() - startTime) / 1000);
    
        // Update the text with elapsed time
        loadingTextElement.text('Loading... (' + elapsedTime + 's)');
    }, 500);
}

function convert_to_date(str) {
    var datePart = str.split('_')[0]
    var timePart = str.split('_')[1]
  
    var year = parseInt(datePart.substring(0, 4))
    var month = parseInt(datePart.substring(5, 7)) - 1 // subtract by 1 due to 0-based Date objects
    var day = parseInt(datePart.substring(8, 10))
    var hour = parseInt(timePart)

    var dateObj = new Date(year, month, day, hour)
    
    console.log(dateObj)
    return dateObj
}

function convert_to_dates(date_strings) {
   return date_strings.map(convert_to_date)
}

function handle_graph_selection(button, graph) {
    graph_type = graph;

    $('.radio').removeClass('btn-primary').addClass('btn-light') // Remove class from all buttons
    $(button).removeClass('btn-light').addClass('btn-primary') // Add class to the clicked button
    console.log("Current graph type " + graph_type);
}

function get_graph_by_date() {
    loading_screen();

    graph_date = dateTimePicker.viewDate
    
    const year = graph_date.getFullYear()
    const month = String(graph_date.getMonth() + 1).padStart(2, "0")
    const day = String(graph_date.getDate()).padStart(2, "0")
    const hours = String(graph_date.getHours()).padStart(2, "0")
    const minutes = String(graph_date.getMinutes()).padStart(2, "0")

    const date_string = `${year}-${month}-${day}_${hours}-${minutes}`

    url = "/graph/" + graph_type + "/" + date_string
    window.location.href = url
}

function get_latest_graph() {
    loading_screen();

    url = "/graph/" + graph_type + "/latest"
    window.location.href = url
}