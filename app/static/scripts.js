let graph_type = "3drefl"
let graph_date = ""

function handle_graph_selection(button, graph) {
    graph_type = graph

    $('.nav-item button').removeClass('bg-danger');
    $('.nav-item button').addClass('bg-primary');
    button.classList.add("bg-danger");
    console.log("Current graph type " + graph_type)
}

function get_graph_by_date() {
    graph_date = dateTimePicker.dates.lastPicked
    console.log("Graph: " + graph_type + " Date: " + graph_date)
}