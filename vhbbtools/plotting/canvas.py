import contextlib2
from rootpy import ROOT
from rootpy.plotting import Canvas as _Canvas

from .tdr_style import TDRStyle


class Canvas(_Canvas):
    """A context manager for a CMS Publication Committee style canvas.

    Credits to Gautier Hamel de Monchenault (Saclay), Joshua Hardenbrook (Princeton),
    and Dinko Ferencek (Rutgers) for the initial Python implementation.

    Entering the context sets the current style to the CMS Technical Design
    Report (TDR) style and returns a canvas with dimensions and margins set to
    default values from the CMS Publication Committee.

    Parameters
    ----------
    name : string, optional
        The name of the canvas. The default is None for a UUID.
    title : string, optional
        The title of the canvas. The default is None for a UUID.
    x : int, optional
        The pixel x-coordinate of the top left corner of the canvas.
        The default is 50.
    y : int, optional
        The pixel y-coordinate of the top left corner of the canvas.
        The default is 50.
    width : int, optional
        The width of the canvas in pixels. The default is 800.
    height : int, optional
        The height of the canvas in pixels. The default is 600.
    size_includes_decorations : bool, optional
        Whether the width and height of the canvas include the size of the window
        manager decorations (the menu and scroll bars). The default is True.
    left_margin : float, optional
        The size of the left margin as a fraction of the canvas width.
        The default is 0.12.
    right_margin : float, optional
        The size of the right margin as a fraction of the canvas width.
        The default is 0.04.
    bottom_margin : float, optional
        The size of the bottom margin as a fraction of the canvas height.
        The default is 0.12.
    top_margin : float, optional
        The size of the top margin as a fraction of the canvas height.
        The default is 0.08
    """
    def __init__(
        self,
        name=None,
        title=None,
        x=50,
        y=50,
        width=800,
        height=600,
        size_includes_decorations=True,
        left_margin=0.12,
        right_margin=0.04,
        bottom_margin=0.12,
        top_margin=0.08,
    ):
        super(Canvas, self).__init__(width, height, x, y, name, title, size_includes_decorations)
        self.SetFillColor(0)
        self.SetBorderMode(0)
        self.SetFrameFillStyle(0)
        self.SetFrameBorderMode(0)
        self.SetTickx(0)
        self.SetTicky(0)
        self.margin = (left_margin, right_margin, bottom_margin, top_margin)

    def __enter__(self):
        """Override the __enter__ method to set the TDR style."""
        with contextlib2.ExitStack() as stack:
            stack.enter_context(TDRStyle())
            self.close = stack.pop_all().close
        return super(Canvas, self).__enter__()

    def __exit__(self, exception_type, exception_value, traceback):
        """Override the __exit__ method to reset the style."""
        super(Canvas, self).__exit__(exception_type, exception_value, traceback)
        self.close()

