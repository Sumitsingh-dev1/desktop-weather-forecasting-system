from dotenv import load_dotenv
load_dotenv()
import sys
import requests
from PyQt5.QtWidgets import QApplication,QWidget,QLabel,QLineEdit,QPushButton,QVBoxLayout,QComboBox

from PyQt5.QtCore import Qt, QThread, pyqtSignal
import os

class WeatherWorker(QThread):
    result_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, city, api_key):
        super().__init__()
        self.city = city
        self.api_key = api_key

    def run(self):
        try:
            # Geocoding API
            geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={self.city},IN&limit=1&appid={self.api_key}"
            geo_response = requests.get(geo_url, timeout=10)
            geo_response.raise_for_status()
            geo_data = geo_response.json()

            if not geo_data:
                self.error_occurred.emit("Location not found")
                return

            lat = geo_data[0]["lat"]
            lon = geo_data[0]["lon"]

            # Weather API
            weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={self.api_key}&units=metric"
            weather_response = requests.get(weather_url, timeout=10)
            weather_response.raise_for_status()

            self.result_ready.emit(weather_response.json())

        except Exception:
            self.error_occurred.emit("Failed to fetch weather")

class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()  
        self.city_label = QLabel("Enter city name:", self)
        self.city_input = QLineEdit(self)
        self.get_weather_button = QPushButton("Get Weather", self)
        self.temperature_label = QLabel(self)
        self.emoji_label = QLabel(self)
        self.description_label = QLabel(self)
        self.status_label = QLabel(self)
        self.history_box = QComboBox(self)
        self.history_box.setPlaceholderText("Search History")
        self.search_history = []
        self.initUI()
       

    def initUI(self):
        self.setWindowTitle("Weather App") 
        self.history_box.currentTextChanged.connect(self.use_history)  

        vbox = QVBoxLayout()


        vbox.addWidget(self.city_label)
        vbox.addWidget(self.city_input) 
        vbox.addWidget(self.history_box)
        vbox.addWidget(self.get_weather_button)
        vbox.addWidget(self.temperature_label)
        vbox.addWidget(self.emoji_label)
        vbox.addWidget(self.description_label)
        vbox.addWidget(self.status_label)
       

        self.setLayout(vbox)

        self.city_label.setAlignment(Qt.AlignCenter) 
        self.city_input.setAlignment(Qt.AlignCenter)
        self.temperature_label.setAlignment(Qt.AlignCenter)
        self.emoji_label.setAlignment(Qt.AlignCenter)
        self.description_label.setAlignment(Qt.AlignCenter)
        self.status_label.setAlignment(Qt.AlignCenter)
        

        self.city_label.setObjectName("city_label")
        self.city_input.setObjectName("city_input")
        self.get_weather_button.setObjectName("get_weather_button")
        self.temperature_label.setObjectName("temperature_label")
        self.emoji_label.setObjectName("emoji_label")
        self.description_label.setObjectName("description_label")

        self.setStyleSheet(""" QLabel,QPushButton
                           {font-family: calibri;}
                           QLabel#city_label{
                           font-size: 40px;
                           font-style: italic;}
                           QLineEdit#city_input{
                           font-size: 40px
                           }
                           QPushButton#get_weather_button{
                            font-size: 30px;
                           font-weight: bold;}
                           QLabel#temperature_label{
                            font-size: 75px;}
                           QLabel#emoji_label{
                            font-size: 100px;
                           font-family: Segoe UI emoji;}

                           QLabel#description_label{
                            font-size: 50px;
                           }
                               """)
        
        self.get_weather_button.clicked.connect(self.get_weather)
        self.city_input.returnPressed.connect(self.get_weather)
        
    
    def get_weather(self):
        city = self.city_input.text().strip()
        api_key = os.getenv("WEATHER_API_KEY")

        if not city:
            self.display_error("Please enter a location")
            return

        self.status_label.setText("Fetching weather...")
        self.get_weather_button.setEnabled(False)

        self.worker = WeatherWorker(city, api_key)
        self.worker.result_ready.connect(self.on_weather_loaded)
        self.worker.error_occurred.connect(self.display_error)
        self.worker.start() 

    def use_history(self, text):
        if text:
            self.city_input.setText(text)
            self.get_weather()    


   
    def on_weather_loaded(self, data):
    # Re-enable button and clear loading text
        self.status_label.setText("")
        self.get_weather_button.setEnabled(True)

        # Get city from input (needed for history)
        city = self.city_input.text().strip()

        if city and city not in self.search_history:
            self.search_history.append(city)
            self.history_box.addItem(city)

        # Show weather result
        self.display_weather(data)

    def display_error(self, message):
        self.status_label.setText("")
        self.get_weather_button.setEnabled(True)

        self.temperature_label.setStyleSheet("font-size: 30px;")
        self.temperature_label.setText(message)
        self.emoji_label.clear()
        self.description_label.clear()                 

    def display_weather(self, data):
        temperature = data["main"]["temp"]
        weather_id = data["weather"][0]["id"]
        description = data["weather"][0]["description"]
        location = data["name"]

        self.temperature_label.setStyleSheet("font-size: 75px;")
        self.temperature_label.setText(f"{temperature:.1f}°C")
        self.emoji_label.setText(self.get_weather_emoji(weather_id))
        self.description_label.setText(f"{location} • {description}")
           

        
             
        
    @staticmethod
    def get_weather_emoji(weather_id):  

        if 200 <=  weather_id <= 232:
            return "🌩️"
        elif 300 <=  weather_id  <= 321:  
            return "☁️"
        elif 500 <=  weather_id  <= 531:
            return "🌧️"
        elif 600 <=  weather_id  <= 622:
            return " ❄️ "
        elif 701 <=  weather_id  <= 741:
            return "🌫️"
        elif  weather_id  == 762:
            return " 🌋  "
        elif  weather_id  == 771:
            return "🌪️"
        elif  weather_id == 781:
            return "🌪️"
        elif   weather_id  == 800:
            return " ☀️ "
        
        elif 801 <=  weather_id  <= 804:
            return " ☁︎ "
        
        else:
            return("")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    Weather_app = WeatherApp()
    Weather_app.show()
    app.exec()