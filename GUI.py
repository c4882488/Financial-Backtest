from flask import Flask, render_template, request
import Main
import KPI
import json
app = Flask(__name__)

# GUI.py成功執行，在瀏覽器輸入http://127.0.0.1:5000/ ，即可看到介面
# 也可直接輸入 http://34.125.202.159/ 進行操作


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/get_data", methods=['POST'])
def get_data():

    stock = request.values['stock']
    KbarsMinutes = int(request.values['KbarsMinutes'])
    KbarsNewHigh = int(request.values['KbarsNewHigh'])
    StopLoss = float(request.values['StopLoss'])
    Main.run(stock, KbarsMinutes, KbarsNewHigh, StopLoss)

    response = app.response_class(
        response=json.dumps(KPI.run()),
        mimetype='application/json'
    )
    return response


if __name__ == "__main__":
    app.run(debug=True)
