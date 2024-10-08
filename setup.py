import sys
from PyQt6.QtWidgets import QApplication
from controlers.MainController import MainController


class App(QApplication):
    def __init__(self, sys_argv):
        super(App, self).__init__(sys_argv)
        self.main_app = MainController()


if __name__ == '__main__':
    app = App(sys.argv)
    sys.exit(app.exec())
