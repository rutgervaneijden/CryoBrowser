from bs4 import BeautifulSoup
from os.path import abspath, dirname, join
from pathlib import Path
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QIcon
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QApplication, QCalendarWidget, QListWidget, QMainWindow, QVBoxLayout, QWidget
from requests import get
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(resource_path('resources/Cryobrowser.png')))
        self.setWindowTitle('Cryobrowser')
        self.calendar = QCalendarWidget()
        self.calendar.clicked.connect(self.date_selected)
        self.available_charts = QListWidget()
        self.date_selected()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.calendar)
        layout.addWidget(self.available_charts)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
    def date_selected(self):
        self.available_charts.clear()
        url = f'https://cryo.met.no/archive/ice-service/icecharts/quicklooks/{self.calendar.selectedDate().toString('yyyy/yyyyMMdd')}'
        response = get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        for link in soup.find_all('a'):
            if link['href'].endswith('.png'):
                self.available_charts.addItem(link['href'])
        # https://noaadata.apps.nsidc.org/NOAA/G02135/north/daily/images/2026/01_Jan/N_20260101_conc_hires_v4.0.png
        # https://noaadata.apps.nsidc.org/NOAA/G02135/south/daily/images/2026/01_Jan/S_20260101_conc_hires_v4.0.png
        # https://noaadata.apps.nsidc.org/NOAA/G02135/north/daily/images/2026/01_Jan/N_20260101_extn_hires_v4.0.png
        # https://noaadata.apps.nsidc.org/NOAA/G02135/south/daily/images/2026/01_Jan/S_20260101_extn_hires_v4.0.png
        for url in [
                f'https://noaadata.apps.nsidc.org/NOAA/G02135/north/daily/images/{self.calendar.selectedDate().toString('yyyy/MM_MMM')}',
                f'https://noaadata.apps.nsidc.org/NOAA/G02135/south/daily/images/{self.calendar.selectedDate().toString('yyyy/MM_MMM')}'
            ]:
            response = get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a'):
                if link['href'].endswith('_conc_hires_v4.0.png') or link['href'].endswith('_extn_hires_v4.0.png'):
                    if link['href'][2:10] == self.calendar.selectedDate().toString('yyyyMMdd'):
                        self.available_charts.addItem(link['href'])
        self.available_charts.itemClicked.connect(self.show_chart)
    def show_chart(self):
        window_id = self.available_charts.currentItem().text()
        globals()[window_id] = ChartWindow()
        globals()[window_id].setWindowTitle(self.available_charts.currentItem().text())
        browser = QWebEngineView()
        browser.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        if not (p / self.available_charts.currentItem().text()).exists():
            with open(p / self.available_charts.currentItem().text(), 'wb') as f:
                if self.available_charts.currentItem().text().startswith('N_'):
                    f.write(get(f'https://noaadata.apps.nsidc.org/NOAA/G02135/north/daily/images/{self.calendar.selectedDate().toString('yyyy/MM_MMM')}/{self.available_charts.currentItem().text()}', stream=True).content)
                if self.available_charts.currentItem().text().startswith('S_'):
                    f.write(get(f'https://noaadata.apps.nsidc.org/NOAA/G02135/south/daily/images/{self.calendar.selectedDate().toString('yyyy/MM_MMM')}/{self.available_charts.currentItem().text()}', stream=True).content)
                if self.available_charts.currentItem().text().endswith('_hat.png') or self.available_charts.currentItem().text().endswith('_col.png'):
                    f.write(get(f'https://cryo.met.no/archive/ice-service/icecharts/quicklooks/{self.calendar.selectedDate().toString('yyyy/yyyyMMdd')}/{self.available_charts.currentItem().text()}', stream=True).content)
        browser.setUrl(QUrl.fromLocalFile(p / self.available_charts.currentItem().text()))
        globals()[window_id].layout.addWidget(browser)
        globals()[window_id].show()

class ChartWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(resource_path('resources/Cryobrowser.png')))
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', dirname(abspath(__file__)))
    return join(base_path, relative_path)

if __name__ == "__main__":
    p = Path('~/Downloads/Cryobrowser').expanduser()
    p.mkdir(exist_ok=True, parents=True)
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()