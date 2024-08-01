from flask import Flask, render_template, request, redirect, url_for
import boto3
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import uuid
import re

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')
dynamodb_client = boto3.client('dynamodb', region_name='ap-southeast-2')


def create_table_if_not_exists(table_name):
    existing_tables = dynamodb.tables.all()
    if table_name not in [table.name for table in existing_tables]:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        return table
    else:
        return dynamodb.Table(table_name)

table = create_table_if_not_exists('data')

import os
import re

def categorize_document(file_path):
    categories = {
        'Structural': {
            'Beams': [],
            'Columns': [],
            'Foundations': [],
            'Slabs': [],
            'Walls': [],
            'Roofs': [],
        },
        'Electrical': {
            'Wiring': [],
            'Lighting': [],
            'Panels': [],
            'Switches': [],
            'Outlets': [],
            'Conduits': [],
        },
        'Plumbing': {
            'Pipes': [],
            'Fixtures': [],
            'Valves': [],
            'Drains': [],
            'Fittings': [],
            'Water Heaters': [],
        },
        'HVAC': {
            'Ducts': [],
            'Vents': [],
            'Thermostats': [],
            'Furnaces': [],
            'Air Conditioners': [],
            'Heat Pumps': [],
        },
        'Finishes': {
            'Flooring': [],
            'Painting': [],
            'Ceilings': [],
            'Trim': [],
            'Doors': [],
            'Windows': [],
        },
        'Exterior': {
            'Siding': [],
            'Roofing': [],
            'Gutters': [],
            'Insulation': [],
            'Masonry': [],
            'Decking': [],
        },
        'Site Work': {
            'Excavation': [],
            'Grading': [],
            'Landscaping': [],
            'Paving': [],
            'Fencing': [],
            'Drainage': [],
        }
    }

    with open(file_path, 'r') as file:
        content = file.read()
        
        # Keyword-based categorization logic
        for line in content.splitlines():
            # Structural
            if re.search(r'\bbeam\b', line, re.IGNORECASE):
                categories['Structural']['Beams'].append(line)
            elif re.search(r'\bcolumn\b', line, re.IGNORECASE):
                categories['Structural']['Columns'].append(line)
            elif re.search(r'\bfoundation\b', line, re.IGNORECASE):
                categories['Structural']['Foundations'].append(line)
            elif re.search(r'\bslab\b', line, re.IGNORECASE):
                categories['Structural']['Slabs'].append(line)
            elif re.search(r'\bwall\b', line, re.IGNORECASE):
                categories['Structural']['Walls'].append(line)
            elif re.search(r'\broof\b', line, re.IGNORECASE):
                categories['Structural']['Roofs'].append(line)
            
            # Electrical
            elif re.search(r'\bwire\b', line, re.IGNORECASE):
                categories['Electrical']['Wiring'].append(line)
            elif re.search(r'\blight\b', line, re.IGNORECASE):
                categories['Electrical']['Lighting'].append(line)
            elif re.search(r'\bpanel\b', line, re.IGNORECASE):
                categories['Electrical']['Panels'].append(line)
            elif re.search(r'\bswitch\b', line, re.IGNORECASE):
                categories['Electrical']['Switches'].append(line)
            elif re.search(r'\boutlet\b', line, re.IGNORECASE):
                categories['Electrical']['Outlets'].append(line)
            elif re.search(r'\bconduit\b', line, re.IGNORECASE):
                categories['Electrical']['Conduits'].append(line)
            
            # Plumbing
            elif re.search(r'\bpipe\b', line, re.IGNORECASE):
                categories['Plumbing']['Pipes'].append(line)
            elif re.search(r'\bfixture\b', line, re.IGNORECASE):
                categories['Plumbing']['Fixtures'].append(line)
            elif re.search(r'\bvalve\b', line, re.IGNORECASE):
                categories['Plumbing']['Valves'].append(line)
            elif re.search(r'\bdrain\b', line, re.IGNORECASE):
                categories['Plumbing']['Drains'].append(line)
            elif re.search(r'\bfitting\b', line, re.IGNORECASE):
                categories['Plumbing']['Fittings'].append(line)
            elif re.search(r'\bwater heater\b', line, re.IGNORECASE):
                categories['Plumbing']['Water Heaters'].append(line)
            
            # HVAC
            elif re.search(r'\bduct\b', line, re.IGNORECASE):
                categories['HVAC']['Ducts'].append(line)
            elif re.search(r'\bvent\b', line, re.IGNORECASE):
                categories['HVAC']['Vents'].append(line)
            elif re.search(r'\bthermostat\b', line, re.IGNORECASE):
                categories['HVAC']['Thermostats'].append(line)
            elif re.search(r'\bfurnace\b', line, re.IGNORECASE):
                categories['HVAC']['Furnaces'].append(line)
            elif re.search(r'\bair conditioner\b', line, re.IGNORECASE):
                categories['HVAC']['Air Conditioners'].append(line)
            elif re.search(r'\bheat pump\b', line, re.IGNORECASE):
                categories['HVAC']['Heat Pumps'].append(line)
            
            # Finishes
            elif re.search(r'\bflooring\b', line, re.IGNORECASE):
                categories['Finishes']['Flooring'].append(line)
            elif re.search(r'\bpaint\b', line, re.IGNORECASE):
                categories['Finishes']['Painting'].append(line)
            elif re.search(r'\bceiling\b', line, re.IGNORECASE):
                categories['Finishes']['Ceilings'].append(line)
            elif re.search(r'\btrim\b', line, re.IGNORECASE):
                categories['Finishes']['Trim'].append(line)
            elif re.search(r'\bdoor\b', line, re.IGNORECASE):
                categories['Finishes']['Doors'].append(line)
            elif re.search(r'\bwindow\b', line, re.IGNORECASE):
                categories['Finishes']['Windows'].append(line)
            
            # Exterior
            elif re.search(r'\bsiding\b', line, re.IGNORECASE):
                categories['Exterior']['Siding'].append(line)
            elif re.search(r'\broof\b', line, re.IGNORECASE):
                categories['Exterior']['Roofing'].append(line)
            elif re.search(r'\bgutter\b', line, re.IGNORECASE):
                categories['Exterior']['Gutters'].append(line)
            elif re.search(r'\binsulation\b', line, re.IGNORECASE):
                categories['Exterior']['Insulation'].append(line)
            elif re.search(r'\bmasonry\b', line, re.IGNORECASE):
                categories['Exterior']['Masonry'].append(line)
            elif re.search(r'\bdeck\b', line, re.IGNORECASE):
                categories['Exterior']['Decking'].append(line)
            
            # Site Work
            elif re.search(r'\bexcavation\b', line, re.IGNORECASE):
                categories['Site Work']['Excavation'].append(line)
            elif re.search(r'\bgrading\b', line, re.IGNORECASE):
                categories['Site Work']['Grading'].append(line)
            elif re.search(r'\blandscaping\b', line, re.IGNORECASE):
                categories['Site Work']['Landscaping'].append(line)
            elif re.search(r'\bpaving\b', line, re.IGNORECASE):
                categories['Site Work']['Paving'].append(line)
            elif re.search(r'\bfencing\b', line, re.IGNORECASE):
                categories['Site Work']['Fencing'].append(line)
            elif re.search(r'\bdrainage\b', line, re.IGNORECASE):
                categories['Site Work']['Drainage'].append(line)
    
    return categories


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        categories = categorize_document(file_path)
        document_id = str(uuid.uuid4())
        
        for category, subcategories in categories.items():
            for subcategory, content in subcategories.items():
                table.put_item(
                    Item={
                        'id': document_id,
                        'category': category,
                        'subcategory': subcategory,
                        'content': ' '.join(content)
                    }
                )
        
        return redirect(url_for('index'))

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
