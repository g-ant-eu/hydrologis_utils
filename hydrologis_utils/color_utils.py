import enum

class ColorProvider():
    """
    A simple color provider class, based on a chosen colortable.
    """
    def __init__(self, colorTableName) -> None:
        """
        constructor
        
        Parameters
        ----------
        colorTableName: str
            The name of the colortable to use.
        """
        self.colorTableName = colorTableName
        self.colorTable = COLORTABLES[colorTableName]
        self.index = 0
        self.max = len(self.colorTable)

    def get_next_hex_color(self):
        """
        Get a color from a table. Starts from begin when reaching the end.
        
        Returns
        -------
        str:
            The next color of the table in hex.
        """
        if self.index == self.max:
            self.index = 0
        color = self.colorTable[self.index]
        self.index += 1
        return color
    
    def get_hex_color_list(self, size):
        """
        Get a list of hex colors.
        
        Parameters
        ----------
        size: int
            the size of the requested list.
        
        Returns
        -------
        list:
            the list of hex colors.
        """
        list = []
        for i in range(size):
            list.append(self.get_next_hex_color())
        return list

class ColorTableNames(enum.Enum):
    """
    Currently available colotables.
    """
    RAINBOW = "rainbow"
    TWELVE_PAIRED = "colorbrewer_twelve_class_paired"
    TWELVE_SET3 = "colorbrewer_twelve_class_set3"
    CHART_COLORS = "chart_colors"
    MAINCOLORS = "main_colors"
    CONTRASTING = "contrasting"
    CONTRASTING130 = "contrasting130"


COLORTABLES = {
    "rainbow":[
        "#FFFF00", 
        "#00FF00", 
        "#00FFFF", 
        "#0000FF", 
        "#FF00FF", 
        "#FF0000"
    ],
    "colorbrewer_twelve_class_paired" :[
        "#a6cee3", 
        "#1f78b4", 
        "#b2df8a", 
        "#33a02c", 
        "#fb9a99", 
        "#e31a1c", 
        "#fdbf6f", 
        "#ff7f00", 
        "#cab2d6", 
        "#6a3d9a", 
        "#b15928", 
        "#ffff99"
    ],
    "colorbrewer_twelve_class_set3" : [
        "#80b1d3", 
        "#fb8072", 
        "#8dd3c7", 
        "#bebada", 
        "#fdb462", 
        "#b3de69", 
        "#fccde5", 
        "#ffffb3", 
        "#d9d9d9", 
        "#bc80bd", 
        "#ccebc5", 
        "#ffed6f" 
    ],
    "main_colors": [
        "#FF0000", 
        "#00FF00", 
        "#0000FF", 
        "#FFFF00", 
        "#00FFFF", 
        "#FF00FF" 
    ],
    "chart_colors" :[
        "#80b1d3", 
        "#fb8072", 
        "#29BF12", 
        "#8dd3c7", 
        "#bebada", 
        "#fdb462", 
        "#507dbc", 
        "#b3de69", 
        "#ffe66d", 
        "#42e2b8", 
        "#fccde5", 
        "#FF5964",
        "#bc80bd", 
        "#ccebc5", 
        "#08BDBD", 
        "#798478", 
        "#2d82b7", 
        "#b2ffd6", 
        "#dce2aa", 
        "#424b54", 
        "#944bbb", 
        "#715b64", 
        "#ceb5a7", 
        "#5b7b7a", 
        "#ffed6f" 
    ],
    "contrasting":[
        "#2E2532", 
        "#210203", 
        "#432818", 
        "#343A1A", 
        "#99582A", 
        "#BB9457", 
        "#BFAE48", 
        "#C9ADA1", 
        "#AB87FF", 
        "#DECDF5", 
        "#084887", 
        "#4D6A6D", 
        "#33658A", 
        "#4D9078", 
        "#28AFB0", 
        "#08BDBD", 
        "#92AFD7", 
        "#B4E1FF", 
        "#B7FDFE", 
        "#5FAD56", 
        "#29BF12", 
        "#ABFF4F", 
        "#B4436C", 
        "#BF3100", 
        "#D33F49", 
        "#F21B3F", 
        "#FF5964", 
        "#F58A07", 
        "#F6AE2D", 
        "#F4D35E", 
        "#FFE74C", 
        "#FFFD98", 
        "#F5FFC6", 
        "#798478", 
        "#898989", 
        "#A0A083", 
        "#E3E3E3", 
        "#F8F1FF", 
        "#F2FDFF" 
    ],
    "contrasting130":[
        "#2E2532", 
        "#210203", 
        "#432818", 
        "#343A1A", 
        "#99582A", 
        "#BB9457", 
        "#BFAE48", 
        "#C9ADA1", 
        "#AB87FF", 
        "#DECDF5", 
        "#084887", 
        "#4D6A6D", 
        "#33658A", 
        "#4D9078", 
        "#28AFB0", 
        "#08BDBD", 
        "#92AFD7", 
        "#B4E1FF", 
        "#B7FDFE", 
        "#5FAD56", 
        "#29BF12", 
        "#ABFF4F", 
        "#B4436C", 
        "#BF3100", 
        "#D33F49", 
        "#F21B3F", 
        "#FF5964", 
        "#F58A07", 
        "#F6AE2D", 
        "#F4D35E", 
        "#FFE74C", 
        "#FFFD98", 
        "#F5FFC6", 
        "#798478", 
        "#898989", 
        "#A0A083", 
        "#E3E3E3", 
        "#F8F1FF", 
        "#F2FDFF", 
        "#93a3b1", 
        "#7c898b", 
        "#636564", 
        "#4c443c", 
        "#322214", 
        "#bcf4f5", 
        "#b4ebca", 
        "#d9f2b4", 
        "#d3fac7", 
        "#ffb7c3", 
        "#a7a5c6", 
        "#8797b2", 
        "#6d8a96", 
        "#5d707f", 
        "#66ced6", 
        "#eef4d4", 
        "#daefb3", 
        "#ea9e8d", 
        "#d64550", 
        "#1c2826", 
        "#5d2a42", 
        "#fb6376", 
        "#fcb1a6", 
        "#ffdccc", 
        "#fff9ec", 
        "#c2efb3", 
        "#97abb1", 
        "#746f72", 
        "#735f3d", 
        "#594a26", 
        "#544b3d", 
        "#4e6e58", 
        "#4c8577", 
        "#a6ece0", 
        "#7adfbb", 
        "#8d3b72", 
        "#8a7090", 
        "#89a7a7", 
        "#72e1d1", 
        "#b5d8cc", 
        "#2d82b7", 
        "#42e2b8", 
        "#f3dfbf", 
        "#eb8a90", 
        "#d7fdf0", 
        "#b2ffd6", 
        "#b4d6d3", 
        "#b8bac8", 
        "#aa78a6", 
        "#944bbb", 
        "#aa7bc3", 
        "#cc92c2", 
        "#dba8ac", 
        "#424b54", 
        "#b38d97", 
        "#d5aca9", 
        "#ebcfb2", 
        "#c5baaf", 
        "#8ed081", 
        "#b4d2ba", 
        "#dce2aa", 
        "#b57f50", 
        "#4b543b", 
        "#bcd4de", 
        "#a5ccd1", 
        "#a0b9bf", 
        "#9dacb2", 
        "#949ba0", 
        "#507dbc", 
        "#a1c6ea", 
        "#bbd1ea", 
        "#dae3e5", 
        "#292f36", 
        "#4ecdc4", 
        "#f7fff7", 
        "#ff6b6b", 
        "#ffe66d", 
        "#8b9474", 
        "#6cae75", 
        "#8bbd8b", 
        "#c1cc99", 
        "#f5a65b", 
        "#d3bdb0", 
        "#c1ae9f", 
        "#89937c", 
        "#715b64", 
        "#69385c", 
        "#e0f2e9", 
        "#ceb5a7", 
        "#a17c6b", 
        "#5b7b7a", 
        "#3c887e" 
    ]

}