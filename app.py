from flask import Flask, render_template, jsonify, request
from sqlalchemy import create_engine, text
import random

app = Flask(__name__)

# Database connection parameters
DATABASE_URI = 'mssql+pyodbc://synthdatauser:6pZ!7+ZuWt@dw-pia-0004057/project?driver=ODBC+Driver+17+for+SQL+Server'

# Create database engine
engine = create_engine(DATABASE_URI, echo=True)

def fetch_and_randomize_data(query, num_rows):
    try:
        with engine.connect() as connection:
            result = connection.execute(text(query))
            columns = result.keys()
            rows = [dict(zip(columns, row)) for row in result]

        if rows:
            # Stronger randomization: shuffle each column independently
            randomized_data = {col: [row[col] for row in rows] for col in columns}
            for col in randomized_data:
                random.shuffle(randomized_data[col])

            # Reassemble rows after shuffling columns
            shuffled_rows = [
                {col: randomized_data[col][i] for col in columns} for i in range(len(rows))
            ]
            return shuffled_rows[:num_rows]  # Limit to the requested number of rows
        else:
            return []

    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_pranaav_data')
def get_pranaav_data():
    num_rows = int(request.args.get('numRows', 10))
    
    query = """
        SELECT
            PAT_MRN_ID,
            PAT_FIRST_NAME,
            PAT_LAST_NAME,
            DOB,
            MOBILE_PHONE_NUMBER,
            PRC_NAME,
            DEPARTMENT_NAME,
            external_department_name,
            APPT_MADE_DATE,
            EFFECTIVE_DATE_DT
        FROM dbo.PranaavData
    """
    
    data = fetch_and_randomize_data(query, num_rows)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
