from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config["SECRET_KEY"] = "8BYkEfBA6O6donzWlSihBXox7C0sKR6b"
Bootstrap(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/create_booking', methods=['POST', 'GET'])
def create_booking():
    if request.method == 'POST':
        room_id = request.form['roomId']
        client_id = request.form['clientId']
        date = request.form['date']
        start_time = request.form['startTime']
        end_time = request.form['endTime']
        
        print(room_id, client_id, date, start_time, end_time)
    return render_template('create_booking.html')

if __name__ == "__main__":
    app.run(debug=True, port=8080)