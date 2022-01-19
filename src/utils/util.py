from threading import Thread

class ThreadWithRetVal(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, daemon=None):
        Thread.__init__(self, group, target, name, args, kwargs, daemon=daemon)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    
    def join(self, *args):
        Thread.join(self, *args)
        return self._return


def make_interpolator(min_range: list, max_range: list): 
    left_span = min_range[-1] - min_range[0]  
    right_span = max_range[-1] - max_range[0]
    scale_factor = float(right_span) / float(left_span) 

    # create interpolation function using pre-calculated scaleFactor
    def interp_fn(value):
        return max_range[0] + (value-min_range[0])*scale_factor

    return interp_fn

def raise_window(window_name: str):

    import win32con
    import win32gui

    def get_window_handle(partial_window_name):

        def window_enumeration_handler(hwnd, windows):
            windows.append((hwnd, win32gui.GetWindowText(hwnd)))

        windows = []
        win32gui.EnumWindows(window_enumeration_handler, windows)

        for i in windows:
            if partial_window_name.lower() in i[1].lower():
                return i                

        print('Window not found!')
        return None

    def bring_window_to_foreground(HWND):
        win32gui.ShowWindow(HWND, win32con.SW_RESTORE)
        win32gui.SetWindowPos(HWND, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)
        win32gui.SetWindowPos(HWND, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)
        win32gui.SetWindowPos(HWND, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_SHOWWINDOW + win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)

    hwnd = get_window_handle(window_name)

    if hwnd is not None:
        bring_window_to_foreground(hwnd[0])