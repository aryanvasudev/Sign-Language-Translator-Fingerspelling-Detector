from flask import Flask, render_template, jsonify, request
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    # Add sign language prediction logic here
    return jsonify({'prediction': 'predicted_word'})

@app.route('/text-to-sign', methods=['POST'])
def text_to_sign():
    text = request.json.get('text')
    # Add text to sign language conversion logic here
    return jsonify({'success': True})




if __name__ == '__main__':
    app.run(debug=True)