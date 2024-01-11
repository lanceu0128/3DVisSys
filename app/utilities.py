
import plotly 
import app

def convertJSONtoHTML(graph_type, target_dir, file_time):
    try:
        # JSONgraph = app.get_dated_graph(target_dir, file_time)
        # fig = plotly.io.read_jsonwith
        with open(f"/data3/lanceu/server/graphs/{graph_type}/{file_time}.json") as f:
            fig = plotly.io.read_json(f)

        file_path = f"/home/lanceu/server/html_graphs/{graph_type}/{file_time}.html"
        plotly.io.write_html(fig=fig, file=file_path)
    except Exception as error:
        print("Exception", str(error))

if __name__ == "__main__":
    convertJSONtoHTML("3Drefl", "/data3/lanceu/server/graphs/3Drefl", "2023-09-08_19")