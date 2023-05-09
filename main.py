import os

from ui.ui_main import show

if __name__ == '__main__':
    if not os.path.exists('temp/report'):
        os.makedirs('temp/report')
    show()