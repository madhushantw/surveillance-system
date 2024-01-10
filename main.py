from config_ui import *

def main():
    app = QApplication(sys.argv)
    window = config_App()
    window.setFixedSize(800, 500)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()