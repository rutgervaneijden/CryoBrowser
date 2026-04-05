# macOS: pyinstaller --icon resources/Cryobrowser.icns -w --add-data 'resources/*:resources' Cryobrowser.py
# Windows: pyinstaller.exe --icon resources/Cryobrowser.ico -F -w --add-data 'resources/*;resources' Cryobrowser.py

import bs4
import os
import PySide6.QtGui
import PySide6.QtWidgets
import PySide6.QtWebEngineWidgets
import requests
import sys

class Charts(PySide6.QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(PySide6.QtGui.QIcon(resource_path('resources/Cryobrowser.png')))
        self.layout = PySide6.QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

class Calendar(PySide6.QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Calendar')
        self.setWindowIcon(PySide6.QtGui.QIcon(resource_path('resources/Cryobrowser.png')))
        self.calendar = PySide6.QtWidgets.QCalendarWidget()
        self.calendar.clicked.connect(self.date_selected)
        self.setCentralWidget(self.calendar)
    def date_selected(self):
        response = requests.get('https://cryo.met.no/archive/ice-service/icecharts/quicklooks/{}'.format(
                self.calendar.selectedDate().toString('yyyy/yyyyMMdd')
            )
        )
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        html = '''
            <!DOCTYPE html>
            <html lang="en">
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width,initial-scale=1">
            <style>
                img { max-width: 100% }
            </style>
            <script>
            </script>
            <body>
        '''
        imgs = set()
        for link in soup.find_all('a'):
            if link['href'].endswith('.png'):
                imgs.add('<img src="https://cryo.met.no/archive/ice-service/icecharts/quicklooks/{}/{}" id="{}" class="{}" />'.format(
                        self.calendar.selectedDate().toString('yyyy/yyyyMMdd'),
                        link['href'],
                        link['href'].split('_')[0],
                        link['href'].split('_')[2]
                    )
                )
        if len(imgs) != 0:
            for img in sorted(list(imgs)):
                html += img
        else:
            html += 'No charts available for this date.'
        html += '''
            </body>
            </html>
        '''
        browser = PySide6.QtWebEngineWidgets.QWebEngineView()
        browser.setHtml(html)
        self.charts = Charts()
        self.charts.layout.addWidget(browser)
        self.charts.setWindowTitle(self.calendar.selectedDate().toString('yyyyMMdd'))
        self.charts.show()

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    app = PySide6.QtWidgets.QApplication([])
    window = Calendar()
    window.show()
    app.exec()