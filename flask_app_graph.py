import base64
from io import BytesIO
from flask import Flask, render_template, request, session, jsonify

# CRITICAL FOR PYTHONANYWHERE: Use the non-interactive Agg backend
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

import pandas as pd

import wordle_counts as wc

import random
import io
#--------------------------------------------------------------------
# Get initial values
#--------------------------------------------------------------------
years = wc.get_years()

app = Flask(__name__)
app.secret_key = 'LG-Wordle-Counts-101'

def plot_graph(x_values, y_values, plot_title):
    plt.plot(x_values,y_values)

    #Use plt.gca() to target the y-axis and set the major locator
    multiplicator_val = (max(y_values) - min(y_values)) // 10
    if multiplicator_val < 1:
        multiplicator_val = 1
    plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(multiplicator_val))

    #annotate
    for x, y in zip(x_values, y_values):
        plt.annotate(f'({x},{y})', xy=(x,y), xytext=(x,y))
    plt.title(plot_title, color="darkblue")
    
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close() # Clear the current figure memory
    buf.seek(0)
    plot_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return plot_base64

def graph_all_counts():
    answers = wc.get_all_answers()
    letter_counts = wc.get_letter_counts(answers)
    y_values = [sum(item) for item in letter_counts]
    plot_title = f"Total Number of times a letter appeared in answers since June 2019"
    plot_base64 = plot_graph(wc.letters, y_values, plot_title)
    return plot_base64

@app.route('/')
def index():
    plot_var = graph_all_counts()
    return render_template('index.html',  years=years, months=wc.month_names, letters=wc.letters, last_date=wc.last_date_str, plot_var=plot_var)

@app.route('/api/show_selected', methods=['POST'])
def show_selected():
    data = request.get_json()
    year = data['year']
    month = data['month']

    if month == "":
        answers = wc.get_answers_for_year(int(year))
        letter_counts = wc.get_letter_counts(answers)
    else:
        letter_counts = wc.get_counts_by_month_for_year(int(year), month)
    y_values = [sum(item) for item in letter_counts]
    plot_title = f"Total Number of times a letter appeared in answers in {year} {month}"
    plot_var = plot_graph(wc.letters, y_values, plot_title)
    return jsonify({'image': plot_var})

if __name__ == '__main__':
    app.run(debug=True)
