from flask import Flask, render_template
from backend.lib import strategies, trades

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/active_strategies')
def active_strategies():
    active_strategies = strategies.display_active_strategies()
    return render_template('active_strategies.html', active_strategies=active_strategies)

if __name__ == '__main__':
    app.run(debug=True)