from flask import Flask, render_template, request, redirect, url_for, flash
from crud_1 import get_vehicles as get_vehicles_1, get_vehicle as get_vehicle_1, create_vehicle as create_vehicle_1, update_vehicle as update_vehicle_1, delete_vehicle as delete_vehicle_1
from database_1 import get_db as get_db_1
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Define a custom filter to format dates
@app.template_filter('format_date')
def format_date(date):
    if date:
        return date.strftime('%d/%m/%Y')
    return ""

@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/index_1')
def index_1():
    db = next(get_db_1())
    search_term = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'brand')
    sort_order = request.args.get('sort_order', 'asc')
    
    # Validate sort_by to prevent SQL injection
    allowed_sort_fields = ['vehicle_type', 'brand', 'commercial_type', 'group_number',
                          'license_plate', 'limit_periodic_inspection', 'kilometer_periodic_inspection',
                          'limit_additional_inspection', 'kilometer_additional_inspection',
                          'date_periodic_inspection', 'date_additional_inspection']
    
    if sort_by not in allowed_sort_fields:
        sort_by = 'brand'
    
    vehicles = get_vehicles_1(db, search=search_term, sort_by=sort_by, direction=sort_order)
    return render_template('index_1.html', 
                         vehicles=vehicles, 
                         search_term=search_term,
                         sort_by=sort_by,
                         sort_order=sort_order)

@app.route('/add_vehicle_1', methods=['GET', 'POST'])
def add_vehicle_1():
    if request.method == 'POST':
        try:
            # Get form data
            vehicle_type = request.form['vehicle_type']
            brand = request.form['brand']
            commercial_type = request.form['commercial_type']
            group_number = int(request.form['group_number']) if request.form['group_number'] else None
            license_plate = request.form['license_plate']
            
            # Handle date fields
            limit_periodic_inspection = datetime.strptime(request.form['limit_periodic_inspection'], '%Y-%m-%d') if request.form['limit_periodic_inspection'] else None
            kilometer_periodic_inspection = int(request.form['kilometer_periodic_inspection']) if request.form['kilometer_periodic_inspection'] else None
            limit_additional_inspection = datetime.strptime(request.form['limit_additional_inspection'], '%Y-%m-%d') if request.form['limit_additional_inspection'] else None
            kilometer_additional_inspection = int(request.form['kilometer_additional_inspection']) if request.form['kilometer_additional_inspection'] else None
            date_periodic_inspection = datetime.strptime(request.form['date_periodic_inspection'], '%Y-%m-%d') if request.form['date_periodic_inspection'] else None
            date_additional_inspection = datetime.strptime(request.form['date_additional_inspection'], '%Y-%m-%d') if request.form['date_additional_inspection'] else None
            
            comments = request.form['comments']

            db = next(get_db_1())
            create_vehicle_1(
                db,
                vehicle_type=vehicle_type,
                brand=brand,
                commercial_type=commercial_type,
                group_number=group_number,
                license_plate=license_plate,
                limit_periodic_inspection=limit_periodic_inspection,
                kilometer_periodic_inspection=kilometer_periodic_inspection,
                limit_additional_inspection=limit_additional_inspection,
                kilometer_additional_inspection=kilometer_additional_inspection,
                date_periodic_inspection=date_periodic_inspection,
                date_additional_inspection=date_additional_inspection,
                comments=comments
            )
            flash('Véhicule ajouté avec succès!', 'success')
            return redirect(url_for('index_1'))
        except Exception as e:
            flash(f'Erreur lors de l\'ajout du véhicule: {str(e)}', 'error')
            return redirect(url_for('add_vehicle_1'))
    
    return render_template('add_vehicle_1.html')

@app.route('/edit_vehicle_1/<int:id>', methods=['GET', 'POST'])
def edit_vehicle_1(id):
    db = next(get_db_1())
    vehicle = get_vehicle_1(db, id)
    
    if request.method == 'POST':
        try:
            # Get form data
            vehicle_type = request.form['vehicle_type']
            brand = request.form['brand']
            commercial_type = request.form['commercial_type']
            group_number = int(request.form['group_number']) if request.form.get('group_number') else None
            license_plate = request.form['license_plate']
            
            # Handle date fields - if field is empty or whitespace, set to None
            limit_periodic_inspection = request.form.get('limit_periodic_inspection')
            limit_periodic_inspection = datetime.strptime(limit_periodic_inspection, '%Y-%m-%d') if limit_periodic_inspection and limit_periodic_inspection.strip() else None
            
            kilometer_periodic_inspection = int(request.form['kilometer_periodic_inspection']) if request.form.get('kilometer_periodic_inspection') else None
            
            limit_additional_inspection = request.form.get('limit_additional_inspection')
            limit_additional_inspection = datetime.strptime(limit_additional_inspection, '%Y-%m-%d') if limit_additional_inspection and limit_additional_inspection.strip() else None
            
            kilometer_additional_inspection = int(request.form['kilometer_additional_inspection']) if request.form.get('kilometer_additional_inspection') else None
            
            date_periodic_inspection = request.form.get('date_periodic_inspection')
            date_periodic_inspection = datetime.strptime(date_periodic_inspection, '%Y-%m-%d') if date_periodic_inspection and date_periodic_inspection.strip() else None
            
            date_additional_inspection = request.form.get('date_additional_inspection')
            date_additional_inspection = datetime.strptime(date_additional_inspection, '%Y-%m-%d') if date_additional_inspection and date_additional_inspection.strip() else None
            
            comments = request.form.get('comments', '')

            update_vehicle_1(
                db,
                id,
                vehicle_type=vehicle_type,
                brand=brand,
                commercial_type=commercial_type,
                group_number=group_number,
                license_plate=license_plate,
                limit_periodic_inspection=limit_periodic_inspection,
                kilometer_periodic_inspection=kilometer_periodic_inspection,
                limit_additional_inspection=limit_additional_inspection,
                kilometer_additional_inspection=kilometer_additional_inspection,
                date_periodic_inspection=date_periodic_inspection,
                date_additional_inspection=date_additional_inspection,
                comments=comments
            )
            flash('Véhicule mis à jour avec succès!', 'success')
            return redirect(url_for('index_1'))
        except Exception as e:
            flash(f'Erreur lors de la mise à jour du véhicule: {str(e)}', 'error')
            return redirect(url_for('edit_vehicle_1', id=id))
    
    return render_template('edit_vehicle_1.html', vehicle=vehicle)


@app.route('/delete_vehicle_1/<int:id>')
def delete_vehicle_route_1(id):
    db = next(get_db_1())
    if delete_vehicle_1(db, id):
        flash('Véhicule supprimé avec succès!', 'success')
    else:
        flash('Erreur lors de la suppression du véhicule.', 'error')
    return redirect(url_for('index_1'))

if __name__ == '__main__':
    app.run(debug=False, port=5003)
