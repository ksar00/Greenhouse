from flask import Flask, render_template, redirect, url_for
import libcamera
from picamera2 import Picamera2, Preview
from datetime import datetime
from sqlite3 import Connection
from matplotlib.figure import Figure
from io import BytesIO
import base64
from time import sleep
import threading
import smbus



class SoilMoist:
    def __init__(self, dry=779, wet=297, i2c_addr=0x4B):
        self.dry = dry
        self.wet = wet
        self.soil_moisture_percent = None
        self.i2c_addr = i2c_addr
        self.bus = smbus.SMBus(1)
        
    def soil_raw_adc(self):
        # Reads word (2 bytes) as int - 0 is comm byte​
        rd = self.bus.read_word_data(self.i2c_addr, 0)
        # Exchanges high and low bytes​
        data = ((rd & 0xFF) << 8) | ((rd & 0xFF00) >> 8)
        # Ignores two least significiant bits​
        data = data >> 2
        return data

    def soil_percent(self):
        data = self.soil_raw_adc()
        if data < self.wet:
            data = 100

        else:
            # tør måling - ADC måling * 100.0 / tør måling - våd måling. ​
            percentage = (self.dry - data) * 100.0 / (self.dry - self.wet) 
            data = round(percentage, 2)
            if percentage < 0:
                data = 0
        if data < 10:
            print(f"Soil is dry and at {data}% moisture!")
        return data
    
    def select_soil_percentage(self, amount):
        if isinstance(amount, int) and amount > 0:
            con = Connection('greenhouse.db')
            cur = con.cursor()
            sql = f"""SELECT moisture_percentage, timestamp FROM SoilMoisture ORDER BY rowid DESC LIMIT {amount}"""
            cur.execute(sql)
            img_rows = cur.fetchall()
            print(img_rows)
            con.close()
            return img_rows
        
    def insert_soilmoisture(self):
        date_time = datetime.now()
        timestamp = f"{date_time.strftime('%d-%m-&Y-%H:%M:%S')}"
        con = Connection('greenhouse.db')
        cur = con.cursor()
        moisture_percentage = self.soil_percent()
        params = (timestamp, moisture_percentage)
        sql = """INSERT INTO SoilMoisture (timestamp, moisture_percentage) VALUES(?, ?)"""
        cur.execute(sql, params)
        con.commit()
        con.close()
        
    def continous_measure(self):
        while True:
            self.soil_moisture_percent = self.soil_percent()
            #print(self.soil_moisture_percent)
            sleep(0.2)
    def start_continous_measure(self):
        soil_thread = threading.Thread(target=self.continous_measure)
        soil_thread.start()

soil_measure = SoilMoist()
soil_measure.insert_soilmoisture()


def select_images(amount):
    if isinstance(amount, int) and amount > 0:
        con = Connection('greenhouse.db')
        cur = con.cursor()
        sql = f"""SELECT timestamp FROM images ORDER BY rowid DESC LIMIT {amount}"""
        cur.execute(sql)
        img_rows = cur.fetchall()
        print(img_rows)
        con.close()
        return img_rows

def insert_img(timestamps):
    con = Connection('greenhouse.db')
    cur = con.cursor()
    params = (timestamps,)
    sql = """INSERT INTO images (timestamp) VALUES(?)"""
    cur.execute(sql, params)
    con.commit()
    con.close()

def take_picture():
    date_time = datetime.now()
    datetime_img = f"{date_time.strftime('%d-%m-%Y-%H:%M:%S')}.jpg"
    picam = Picamera2()
    config = picam.create_preview_configuration(main={"size": (640,480)})
    config["transform"] = libcamera.Transform(hflip=1, vflip=1)
    picam.configure(config)
    picam.start()
    picam.capture_file(f"static/img/{datetime_img}")
    picam.close()
    insert_img(datetime_img)

take_picture()

app = Flask(__name__)

@app.route("/soil/")
def soil():
    soil_data = soil_measure.select_soil_percentage(10)
    fig = Figure()
    ax = fig.subplots()
    x = []
    y = []
    ax.tick_params(axis='x', which='both', rotation=30)
    fig.subplots_adjust(bottom=0.3)
    ax.set_xlabel("Timestamps")
    ax.set_ylabel("Soilmoisture %")
    for row in soil_data:
        x.append(row[1]) #timestamp
        y.append(row[0]) # moisture percentage
    ax.plot(x, y)
    buf = BytesIO()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return render_template("soil.html", soil_data = data)


@app.route("/take_photo/")
def take_photo():
    take_picture
    return redirect(url_for("home"))

@app.route("/")
def home():
    return render_template("home.html", image = select_images(1)[0][0])

@app.route("/gallery/")
def gallery():
    image_rows = select_images(10)
    return render_template("gallery.html", image_rows = image_rows)

@app.route("/site2/")
def site2():
    return render_template("site2.html")

if __name__ == ('__main__'):
    app.run(host="0.0.0.0", debug=True)
