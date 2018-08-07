from KnowledgeConnector import graph_controler
from KnowledgeViewer.queries import *
from KnowledgeViewer.plots import basicFigures as figure
from KnowledgeViewer.analyses import basicAnalysis as analyses

def getDBresults(query, driver, replace=[]):
    for r,by in replace:
        query = query.replace(r,by)
    results = graph_controler.getCursorData(driver, query)
    print(results)
    return results

def getPlot(name, data, identifier, title, args = {}):
    plot = None
    if name == "basicTable":
        colors = ('#C2D4FF','#F5F8FF')
        attr =  {'width':800, 'height':300, 'font':12}
        subset = None
        if "colors" in args:
            colors = args["colors"]
        if "attr" in args:
            attr = args["attr"]
        if "subset" in args:
            subset = args["subset"]
        plot = figure.getBasicTable(data, identifier, title, colors=colors, subset=subset, plot_attr=attr)
    elif name == "basicBarPlot":
        print(data.columns)
        if "x" in data.columns and "y" in data.columns and "name" in data.columns:
            x_title = "x"
            y_title = "y"
            if "x_title" in args:
                x_title = args["x_title"]
            if "y_title" in args:
                y_title = args["y_title"]
            plot = figure.getBarPlotFigure(data, identifier, title, x_title, y_title)
    elif name == "scatterPlot":
        if "x" in data.columns and "y" in data.columns and "name" in data.columns:
            x_title = "x"
            y_title = "y"
            if "x_title" in args:
                x_title = args["x_title"]
            if "y_title" in args:
                y_title = args["y_title"]
            plot = figure.getScatterPlotFigure(data, identifier, x_title, y_title, title)

    return plot

def getAnalysisResults(qtype, data, args):
    if qtype == "proteomics":
        imputation = True
        method = "distribution"
        missing_method = 'percentage'
        missing_max = 0.3
        if "imputation" in args:
            imputation = args["imputation"]
        if "method" in args:
            method = args["method"]
        if "missing_method" in args:
            missing_method = args["missing_method"]
        if "missing_max" in args:
            missing_max = args["missing_max"]
        print("Before", data.shape)
        data = analyses.get_measurements_ready(data, imputation = imputation, method = method, missing_method = missing_method, missing_max = missing_max)
        print("After", data.shape)
        

def view(title, section_query, analysis_type, plot_name, args):
    result = None
    plot = None
    driver = graph_controler.getGraphDatabaseConnectionConfiguration()
    if title in ["project","proteomics"]:
        replace = []
        queries = project_cypher.queries
        replacement = "PROJECTID"
        if "id" in args:
            replace.append((replacement, args["id"]))
            print("Here",section_query)
            query = None
            if section_query.upper() in queries:
                plot_title, query = queries[section_query.upper()]
                data = getDBresults(query, driver, replace)
                result = data
                if not data.empty:
                    if analysis_type is not None:
                        result = getAnalysisResults(title, result, args)
                if not result.empty:
                    plot = getPlot(plot_name, result, "project_"+section_query, plot_title, args)
    elif title == "import":
        pass

    return plot
    

    