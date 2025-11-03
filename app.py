from flask import Flask, Blueprint

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('templates/index.html')

if __name__ == '__main__':
    app.run(debug=True)