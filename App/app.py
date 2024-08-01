from flask import Flask, request, render_template, redirect, url_for, flash
import boto3
import os
import PyPDF2
from werkzeug.utils import secure_filename
from botocore.exceptions import ClientError

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
DYNAMODB_TABLE_NAME = 'PDFContentTable'

# Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = '123456789987654321'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB

dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_dynamodb_table(table_name):
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'file_name',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'file_name',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        print(f"Table {table_name} created successfully.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"Table {table_name} already exists.")
        else:
            print(f"Unexpected error: {e}")
            raise

def insert_data_into_dynamodb(table_name, file_name, text):
    table = dynamodb.Table(table_name)
    table.put_item(
        Item={
            'file_name': file_name,
            'text': text
        }
    )

def extract_text_from_pdf(file_path):
    text_data = ""
    with open(file_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                text_data += text
    return text_data

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Create DynamoDB table if not exists
            create_dynamodb_table(DYNAMODB_TABLE_NAME)
            
            # Extract text and insert into DynamoDB
            text_data = extract_text_from_pdf(file_path)
            insert_data_into_dynamodb(DYNAMODB_TABLE_NAME, filename, text_data)
            
            flash('File successfully uploaded and processed')
            return redirect(url_for('upload_file'))
    return render_template('upload.html')

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
