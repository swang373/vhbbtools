from rootpy import ROOT
from rootpy.plotting.style import Style, get_style, set_style


class TDRStyle(Style):
    """The CMS Technical Design Report (TDR) plotting style.

    Unused styling options in the original definition have been removed
    for clarity.
    """
    def __init__(self):
        super(TDRStyle, self).__init__('tdrStyle', 'Style for P-TDR')
        # Canvas
        self.SetCanvasBorderMode(0)
        self.SetCanvasColor(0)
        self.SetCanvasDefH(600) # Height
        self.SetCanvasDefW(600) # Width
        self.SetCanvasDefX(0) # On-Screen Position
        self.SetCanvasDefY(0)
        # Pad
        self.SetPadBorderMode(0)
        self.SetPadColor(0)
        self.SetPadGridX(False)
        self.SetPadGridY(False)
        self.SetGridColor(0)
        self.SetGridStyle(3)
        self.SetGridWidth(1)
        # Frame
        self.SetFrameBorderMode(0)
        self.SetFrameBorderSize(1)
        self.SetFrameFillColor(0)
        self.SetFrameFillStyle(0)
        self.SetFrameLineColor(1)
        self.SetFrameLineStyle(1)
        self.SetFrameLineWidth(1)
        # Histogram
        self.SetHistLineColor(1)
        self.SetHistLineStyle(0)
        self.SetHistLineWidth(1)
        self.SetEndErrorSize(2)
        self.SetMarkerStyle(20)
        # Fit/Function
        self.SetOptFit(1)
        self.SetFitFormat('5.4g')
        self.SetFuncColor(2)
        self.SetFuncStyle(1)
        self.SetFuncWidth(1)
        # Date
        self.SetOptDate(0)
        # Statistics Box
        self.SetOptFile(0)
        self.SetOptStat(0) # Pass 'mr' to display the mean and RMS.
        self.SetStatColor(0)
        self.SetStatFont(42)
        self.SetStatFontSize(0.025)
        self.SetStatTextColor(1)
        self.SetStatFormat('6.4g')
        self.SetStatBorderSize(1)
        self.SetStatH(0.1)
        self.SetStatW(0.15)
        # Margins
        self.SetPadTopMargin(0.05)
        self.SetPadBottomMargin(0.13)
        self.SetPadLeftMargin(0.16)
        self.SetPadRightMargin(0.02)
        # Global Title
        self.SetOptTitle(0) # 0 = No Title
        self.SetTitleFont(42)
        self.SetTitleColor(1)
        self.SetTitleTextColor(1)
        self.SetTitleFillColor(10)
        self.SetTitleFontSize(0.05)
        # Axis Titles
        self.SetTitleColor(1, 'XYZ')
        self.SetTitleFont(42, 'XYZ')
        self.SetTitleSize(0.06, 'XYZ')
        self.SetTitleXOffset(0.9)
        self.SetTitleYOffset(1.25)
        # Axis Labels
        self.SetLabelColor(1, 'XYZ')
        self.SetLabelFont(42, 'XYZ')
        self.SetLabelOffset(0.007, 'XYZ')
        self.SetLabelSize(0.05, 'XYZ')
        # Axes
        self.SetAxisColor(1, 'XYZ')
        self.SetStripDecimals(True)
        self.SetTickLength(0.03, 'XYZ')
        self.SetNdivisions(510, 'XYZ')
        self.SetPadTickX(1) # 0 = Text labels (and ticks) only on bottom, 1 = Text labels on top and bottom
        self.SetPadTickY(1)
        # Log Scale Axes
        self.SetOptLogx(0)
        self.SetOptLogy(0)
        self.SetOptLogz(0)
        # Postscript Options
        self.SetPaperSize(20, 20)
        # Hatches
        self.SetHatchesLineWidth(5)
        self.SetHatchesSpacing(0.05)

    def __enter__(self):
        """Override the __enter__ method to remember the current gStyle.
        """
        self.old_gStyle = get_style(ROOT.gStyle.name)
        set_style(self)
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """Override the __exit__ method to reset to the original gStyle.
        """
        set_style(self.old_gStyle)

