import argparse

def File_Input(Name, InputPath = "", extension = ".csv", separator = ",", IgnoreLines = 0, ImportLegend = True):
    #Arguments for file name are split into three variables, if path is not specified, current dirrectory will be used. Extension is stored seperately, because output graph will use the same name as input file
    FileName = InputPath + Name + extension

    f = open(FileName)

    #Ignores some amount of lines specified by input parameter. Used to ignore metadata before actual csv measurements.
    for i in range(IgnoreLines):
        f.readline()
    Line = f.readline()
    
    columns = Line.count(separator) + 1 #Counts the number of separators to identift the number of columns, there should be one more column than the number of separators per line.
    
    #Importing legend/axis names, if ImportLegend set to True
    if (ImportLegend): 
        Legend = []
        LegendItem = ""
        for i in Line:
            if i != separator:
                LegendItem += i
            else:
                Legend.append(LegendItem)
                LegendItem = ""
        Legend.append(LegendItem[:-1])
    
    #Importing data in format Data = [[Row1], [Row2], ...]
    Data = []
    Row = []
    item = ""
    for line in f:
        for i in line:
            if i != separator:
                item += i 
            else:
                Row.append(float(item))
                item = ""
        Row.append(float(item))
        Data.append(Row)
        Row = []
        item = ""
    
    f.close()
    if ImportLegend:
        return(Data, Legend)
    else:
        return(Data)

def get_column(data, index):
    return [row[index] for row in data]

def Plot(Data, Legend, Name, SavePlotToFile = True, FigureSize = (8, 6), CustomYLabel = False, CustomXLabel = False, YLabel = "y(x)", XLabel = "x", colX = 0, colY = [1], CustomXRange = False, CustomYRange = False, XRange = (0, 1), YRange = (0, 1), EngNotation = True, ImportLegend = True):
    
    import matplotlib.pyplot as plt
    from matplotlib.ticker import EngFormatter
    
    fig, ax = plt.subplots(figsize = FigureSize)
    ax.grid(True)
    
    #Sets X and Y axis labels.
    if ImportLegend:
        if not CustomXLabel:
            ax.set_xlabel(Legend[colX])
        else:
            ax.set_xlabel(XLabel)
        if not CustomYLabel:
            ax.set_ylabel(Legend[colY[0]])
        else:
            ax.set_ylabel(YLabel)
    else:
        ax.set_xlabel(XLabel)
        ax.set_ylabel(YLabel)
    
    #Sets range for X and Y axes.
    if CustomXRange:
        ax.set_xlim(XRange)
    
    if CustomYRange:
        ax.set_ylim(YRange)
    
    #Switches to engineering notation for both axes.
    if EngNotation:
        ax.xaxis.set_major_formatter(EngFormatter())
        ax.yaxis.set_major_formatter(EngFormatter())
    
    #Plots the data with or without legend depending on whether the legend was imported.
    for i in colY:
        if ImportLegend:
            ax.plot(get_column(Data, colX), get_column(Data, i), label = Legend[i])
        else:
            ax.plot(get_column(Data, colX), get_column(Data, i))
    
    #Legend will be in top right corner, it is set to be transparent in order to not hide data.
    if ImportLegend:
        ax.legend(framealpha = 0.5)
    
    if SavePlotToFile:
        fig.savefig(Name+".pdf")

def LatexTable(Data, Legend, Columns, caption = "", label = None, Range = None, Frequency = None, SampleColumn = False, ImportLegend = True):
    #Making A latex table.
    
    SetLabel = True
    if label is None:
        SetLabel = False
    
    
    Centering = "|"
    for i in Columns:
        Centering +="c|"
    
    if ImportLegend:
        Header = ""
        for i in Columns:
            Header += Legend[i] + " & "
        Header = Header[:-3]
    
    if Range is not None:
        start = Range [0]
        stop = Range [1]
    else:
        start = 0
        stop = len(Data) -1
    
    print (r"\begin{table}[H]")
    print (r"\centering")
    print (fr"\caption{{{caption}}}")
    print (fr"\label{{tab:{label}}}")
    print (fr"\begin{{tabular}}{{{Centering}}}")
    print (r"\hline")
    if ImportLegend:
        print (fr"{Header}\\")
        print (r"\hline")
    
    for j in range(start, stop, Frequency if Frequency is not None else 1):
        line = ""
        for i in Columns:
            if i == 0 and SampleColumn:
                line += str(int(Data[j][i])) + " & "
            else:
                line += str(f"{Data[j][i]:.3f} & ")
        line = line[:-3] + r"\\ \hline"
        print(line)
    
    print (r"\end{tabular}")
    print (r"\end{table}")

def main():
    parser = argparse.ArgumentParser(
        description="CSV Visualizer: reads CSV files, generates plots and LaTeX tables."
    )

    # -------------------------------
    # File Input Options
    # -------------------------------
    parser.add_argument(
        "--name",
        required=True,
        help="Name of the CSV file (without extension) [REQUIRED]"
    )
    parser.add_argument(
        "--inputpath",
        default="",
        help="Path to CSV file. If none specified, current directory will be used [default='']"
    )
    parser.add_argument(
        "--extension",
        default=".csv",
        help="Input file extension [default='.csv']"
    )
    parser.add_argument(
        "--separator",
        default=",",
        help="CSV separator character [default=',']"
    )
    parser.add_argument(
        "--ignorelines",
        type=int,
        default=0,
        help="Lines to ignore at start [default=0]"
    )
    parser.add_argument(
        "--importlegend",
        type=int,
        choices=[0, 1],
        default=1,
        help="Import legend (1=True, 0=False) [default=1]"
    )

    # -------------------------------
    # Plot Options
    # -------------------------------
    parser.add_argument(
        "--plot",
        type=int,
        choices=[0, 1],
        default=1,
        help="Generate plot (1=True, 0=False) [default=1]"
    )
    parser.add_argument(
        "--colx",
        type=int,
        default=0,
        help="Column for X axis [default=0]"
    )
    parser.add_argument(
        "--coly",
        type=int,
        nargs="+",
        default=[1],
        help="Column(s) for Y axis [default=1]"
    )
    parser.add_argument(
        "--figuresize",
        type=float,
        nargs=2,
        default=[8, 6],
        help="Figure size as width height [default=8 6]"
    )
    parser.add_argument(
        "--customxlabel",
        type=int,
        choices=[0, 1],
        default=0,
        help="Use custom X axis label (1=True, 0=False) [default=0]"
    )
    parser.add_argument(
        "--customylabel",
        type=int,
        choices=[0, 1],
        default=0,
        help="Use custom Y axis label (1=True, 0=False) [default=0]"
    )
    parser.add_argument(
        "--xlabel",
        default="x",
        help="Custom X axis label (used if --customxlabel=1) [default='x']"
    )
    parser.add_argument(
        "--ylabel",
        default="y(x)",
        help="Custom Y axis label (used if --customylabel=1) [default='y(x)']"
    )
    parser.add_argument(
        "--customxrange",
        type=float,
        nargs=2,
        help="Custom X axis range (start stop) [optional]"
    )
    parser.add_argument(
        "--customyrange",
        type=float,
        nargs=2,
        help="Custom Y axis range (start stop) [optional]"
    )
    parser.add_argument(
        "--engnotation",
        type=int,
        choices=[0, 1],
        default=1,
        help="Use engineering notation on axes (1=True, 0=False) [default=1]"
    )

    # -------------------------------
    # LaTeX Table Options
    # -------------------------------
    parser.add_argument(
        "--maketable",
        type=int,
        choices=[0, 1],
        default=1,
        help="Generate LaTeX table (1=True, 0=False) [default=1]"
    )
    parser.add_argument(
        "--columns",
        type=int,
        nargs="+",
        default=[0, 1, 2, 3],
        help="Which columns to include for LaTeX table [default=0 1 2 3]"
    )
    parser.add_argument(
        "--frequency",
        type=int,
        default=1,
        help="Frequency for LaTeX table rows (use every nth row) [default=1]"
    )
    parser.add_argument(
        "--range",
        type=float,
        nargs=2,
        help="Start and stop rows for LaTeX table (will be converted to int) [optional]"
    )
    parser.add_argument(
        "--samplecolumn",
        type=int,
        choices=[0, 1],
        default=0,
        help="Convert first column to int for LaTeX table (1=True, 0=False) [default=0]"
    )

    args = parser.parse_args()

    # Convert importlegend, samplecolumn, custom label, engnotation flags to bool
    ImportLegend = bool(args.importlegend)
    SampleColumn = bool(args.samplecolumn)
    CustomXLabel = bool(args.customxlabel)
    CustomYLabel = bool(args.customylabel)
    EngNotation = bool(args.engnotation)

    # Read CSV
    Data, Legend = File_Input(
        Name=args.name,
        InputPath=args.inputpath,
        extension=args.extension,
        separator=args.separator,
        IgnoreLines=args.ignorelines,
        ImportLegend=ImportLegend
    )

    # Plot
    if args.plot:
        Plot(
            Data=Data,
            Legend=Legend,
            Name=args.name,
            SavePlotToFile=True,
            FigureSize=tuple(args.figuresize),
            CustomXLabel=CustomXLabel,
            CustomYLabel=CustomYLabel,
            XLabel=args.xlabel,
            YLabel=args.ylabel,
            colX=args.colx,
            colY=args.coly,
            CustomXRange=args.customxrange is not None,
            CustomYRange=args.customyrange is not None,
            XRange=tuple(args.customxrange) if args.customxrange else (0, 1),
            YRange=tuple(args.customyrange) if args.customyrange else (0, 1),
            EngNotation=EngNotation,
            ImportLegend=ImportLegend
        )

    # LaTeX Table
    if args.maketable:
        LatexTable(
            Data=Data,
            Columns=args.columns,
            Legend=Legend,
            Range=args.range,
            Frequency=args.frequency,
            SampleColumn=SampleColumn,
            ImportLegend=ImportLegend
        )

if __name__ == "__main__":
    main()