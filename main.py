from flask import Flask, render_template, request, redirect, url_for, flash
from database_1 import get_db as get_db_1, init_db as init_db_1
from database_2 import get_db as get_db_2, init_db as init_db_2

from crud_1 import (
    get_vehicles as get_vehicles_1, create_vehicle as create_vehicle_1,
    get_vehicle as get_vehicle_1, delete_vehicle as delete_vehicle_1,
    update_vehicle as update_vehicle_1
)
from crud_2 import (
    get_vehicles_2, create_vehicle as create_vehicle_2,
    get_vehicle as get_vehicle_2, delete_vehicle as delete_vehicle_2,
    update_vehicle as update_vehicle_2
)
from datetime import datetime
import logging

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/index_1')
def index_1():
    try:
        db = next(get_db_1())
        search_term = request.args.get('search', '')
        sort_by = request.args.get('sort_by', 'brand')
        sort_order = request.args.get('sort_order', 'asc')
        
        vehicles = get_vehicles_1(db, 0, 100, search_term, sort_by, sort_order)
        return render_template('index_1.html', vehicles=vehicles, search_term=search_term,
                             sort_by=sort_by, sort_order=sort_order)
    except Exception as e:
        logger.error(f"Error in index_1: {str(e)}")
        flash('Une erreur est survenue lors du chargement des véhicules.', 'danger')
        return render_template('index_1.html', vehicles=[], search_term='',
                             sort_by='brand', sort_order='asc')

@app.route('/index_2')
def index_2():
    try:
        db = next(get_db_2())
        search_term = request.args.get('search', '')
        sort_by = request.args.get('sort_by', 'brand')
        sort_order = request.args.get('sort_order', 'asc')
        
        vehicles = get_vehicles_2(db, 0, 100, search_term, sort_by, sort_order)
        return render_template('index_2.html', vehicles=vehicles, search_term=search_term,
                             sort_by=sort_by, sort_order=sort_order)
    except Exception as e:
        logger.error(f"Error in index_2: {str(e)}")
        flash('Une erreur est survenue lors du chargement des véhicules.', 'danger')
        return render_template('index_2.html', vehicles=[], search_term='',
                             sort_by='brand', sort_order='asc')


@app.route('/add_vehicle_1', methods=['GET', 'POST'])
def add_vehicle_1():
    if request.method == 'POST':
        try:
            db = next(get_db_1())
            vehicle_data = {
                'vehicle_type': request.form['vehicle_type'],
                'brand': request.form['brand'],
                'commercial_type': request.form['commercial_type'],
                'group_number': request.form['group_number'] if request.form['group_number'] else None,
                'license_plate': request.form['license_plate'],
                'limit_periodic_inspection': datetime.strptime(request.form['limit_periodic_inspection'], '%Y-%m-%d') if request.form['limit_periodic_inspection'] else None,
                'kilometer_periodic_inspection': int(request.form['kilometer_periodic_inspection']) if request.form['kilometer_periodic_inspection'] else None,
                'limit_additional_inspection': datetime.strptime(request.form['limit_additional_inspection'], '%Y-%m-%d') if request.form['limit_additional_inspection'] else None,
                'kilometer_additional_inspection': int(request.form['kilometer_additional_inspection']) if request.form['kilometer_additional_inspection'] else None,
                'date_periodic_inspection': datetime.strptime(request.form['date_periodic_inspection'], '%Y-%m-%d') if request.form['date_periodic_inspection'] else None,
                'date_additional_inspection': datetime.strptime(request.form['date_additional_inspection'], '%Y-%m-%d') if request.form['date_additional_inspection'] else None,
                'comments': request.form.get('comments', '')
            }
            
            create_vehicle_1(db, **vehicle_data)
            flash('Véhicule ajouté avec succès!', 'success')
            return redirect(url_for('index_1'))
        except KeyError as e:
            logger.error(f"Missing form field in add_vehicle_1: {str(e)}")
            flash('Tous les champs requis doivent être remplis.', 'danger')
        except ValueError as e:
            logger.error(f"Invalid value in add_vehicle_1: {str(e)}")
            flash('Certaines valeurs sont invalides. Vérifiez les champs numériques et les dates.', 'danger')
        except Exception as e:
            logger.error(f"Error in add_vehicle_1: {str(e)}")
            flash('Une erreur est survenue lors de l\'ajout du véhicule.', 'danger')
    
    return render_template('add_vehicle_1.html')

@app.route('/add_vehicle_2', methods=['GET', 'POST'])
def add_vehicle_2():
    if request.method == 'POST':
        try:
            db = next(get_db_2())
            vehicle_data = {
                'vehicle_type': request.form['vehicle_type'],
                'brand': request.form['brand'],
                'commercial_type': request.form['commercial_type'],
                'group_number': request.form['group_number'] if request.form['group_number'] else None,
                'license_plate': request.form['license_plate'],
                'work_with': request.form.get('work_with'),
                'kilometer_additional_inspection': int(request.form['kilometer_additional_inspection']) if request.form['kilometer_additional_inspection'] else None,
                'ct_soeco_date': datetime.strptime(request.form['ct_soeco_date'], '%Y-%m-%d') if request.form['ct_soeco_date'] else None,
                'euromaster_chrono': datetime.strptime(request.form['euromaster_chrono'], '%Y-%m-%d') if request.form['euromaster_chrono'] else None,
                'euromaster_limiteur': datetime.strptime(request.form['euromaster_limiteur'], '%Y-%m-%d') if request.form['euromaster_limiteur'] else None,
                'ned92_chrono': datetime.strptime(request.form['ned92_chrono'], '%Y-%m-%d') if request.form['ned92_chrono'] else None,
                'ned92_limiteur': datetime.strptime(request.form['ned92_limiteur'], '%Y-%m-%d') if request.form['ned92_limiteur'] else None,
                'date_technical_inspection': datetime.strptime(request.form['date_technical_inspection'], '%Y-%m-%d') if request.form['date_technical_inspection'] else None,
                'date_chrono': datetime.strptime(request.form['date_chrono'], '%Y-%m-%d') if request.form['date_chrono'] else None,
                'date_limiteur': datetime.strptime(request.form['date_limiteur'], '%Y-%m-%d') if request.form['date_limiteur'] else None,
                'comments': request.form.get('comments', '')
            }
            
            create_vehicle_2(db, **vehicle_data)
            flash('Véhicule ajouté avec succès!', 'success')
            return redirect(url_for('index_2'))
        except KeyError as e:
            logger.error(f"Missing form field in add_vehicle_2: {str(e)}")
            flash('Tous les champs requis doivent être remplis.', 'danger')
        except ValueError as e:
            logger.error(f"Invalid value in add_vehicle_2: {str(e)}")
            flash('Certaines valeurs sont invalides. Vérifiez les champs numériques et les dates.', 'danger')
        except Exception as e:
            logger.error(f"Error in add_vehicle_2: {str(e)}")
            flash('Une erreur est survenue lors de l\'ajout du véhicule.', 'danger')
    
    return render_template('add_vehicle_2.html')

@app.route('/edit_vehicle_1/<int:id>', methods=['GET', 'POST'])
def edit_vehicle_1(id):
    try:
        db = next(get_db_1())
        vehicle = get_vehicle_1(db, id)
        
        if not vehicle:
            flash('Véhicule non trouvé.', 'danger')
            return redirect(url_for('index_1'))
        
        if request.method == 'POST':
            try:
                vehicle_data = {
                    'vehicle_type': request.form['vehicle_type'],
                    'brand': request.form['brand'],
                    'commercial_type': request.form['commercial_type'],
                    'group_number': request.form['group_number'] if request.form['group_number'] else None,
                    'license_plate': request.form['license_plate'],
                    'limit_periodic_inspection': datetime.strptime(request.form['limit_periodic_inspection'], '%Y-%m-%d') if request.form['limit_periodic_inspection'] else None,
                    'kilometer_periodic_inspection': int(request.form['kilometer_periodic_inspection']) if request.form['kilometer_periodic_inspection'] else None,
                    'limit_additional_inspection': datetime.strptime(request.form['limit_additional_inspection'], '%Y-%m-%d') if request.form['limit_additional_inspection'] else None,
                    'kilometer_additional_inspection': int(request.form['kilometer_additional_inspection']) if request.form['kilometer_additional_inspection'] else None,
                    'date_periodic_inspection': datetime.strptime(request.form['date_periodic_inspection'], '%Y-%m-%d') if request.form['date_periodic_inspection'] else None,
                    'date_additional_inspection': datetime.strptime(request.form['date_additional_inspection'], '%Y-%m-%d') if request.form['date_additional_inspection'] else None,
                    'comments': request.form.get('comments', '')
                }
                
                update_vehicle_1(db, id, **vehicle_data)
                flash('Véhicule mis à jour avec succès!', 'success')
                return redirect(url_for('index_1'))
            except KeyError as e:
                logger.error(f"Missing form field in edit_vehicle_1: {str(e)}")
                flash('Tous les champs requis doivent être remplis.', 'danger')
            except ValueError as e:
                logger.error(f"Invalid value in edit_vehicle_1: {str(e)}")
                flash('Certaines valeurs sont invalides. Vérifiez les champs numériques et les dates.', 'danger')
            except Exception as e:
                logger.error(f"Error in edit_vehicle_1: {str(e)}")
                flash('Une erreur est survenue lors de la mise à jour du véhicule.', 'danger')
        
        return render_template('edit_vehicle_1.html', vehicle=vehicle)
    except Exception as e:
        logger.error(f"Error loading vehicle in edit_vehicle_1: {str(e)}")
        flash('Une erreur est survenue lors du chargement du véhicule.', 'danger')
        return redirect(url_for('index_1'))

@app.route('/edit_vehicle_2/<int:id>', methods=['GET', 'POST'])
def edit_vehicle_2(id):
    try:
        db = next(get_db_2())
        vehicle = get_vehicle_2(db, id)
        
        if not vehicle:
            flash('Véhicule non trouvé.', 'danger')
            return redirect(url_for('index_2'))
        
        if request.method == 'POST':
            try:
                vehicle_data = {
                    'vehicle_type': request.form['vehicle_type'],
                    'brand': request.form['brand'],
                    'commercial_type': request.form['commercial_type'],
                    'group_number': request.form['group_number'] if request.form['group_number'] else None,
                    'license_plate': request.form['license_plate'],
                    'work_with': request.form.get('work_with'),
                    'kilometer_additional_inspection': int(request.form['kilometer_additional_inspection']) if request.form['kilometer_additional_inspection'] else None,
                    'ct_soeco_date': datetime.strptime(request.form['ct_soeco_date'], '%Y-%m-%d') if request.form['ct_soeco_date'] else None,
                    'euromaster_chrono': datetime.strptime(request.form['euromaster_chrono'], '%Y-%m-%d') if request.form['euromaster_chrono'] else None,
                    'euromaster_limiteur': datetime.strptime(request.form['euromaster_limiteur'], '%Y-%m-%d') if request.form['euromaster_limiteur'] else None,
                    'ned92_chrono': datetime.strptime(request.form['ned92_chrono'], '%Y-%m-%d') if request.form['ned92_chrono'] else None,
                    'ned92_limiteur': datetime.strptime(request.form['ned92_limiteur'], '%Y-%m-%d') if request.form['ned92_limiteur'] else None,
                    'date_technical_inspection': datetime.strptime(request.form['date_technical_inspection'], '%Y-%m-%d') if request.form['date_technical_inspection'] else None,
                    'date_chrono': datetime.strptime(request.form['date_chrono'], '%Y-%m-%d') if request.form['date_chrono'] else None,
                    'date_limiteur': datetime.strptime(request.form['date_limiteur'], '%Y-%m-%d') if request.form['date_limiteur'] else None,
                    'comments': request.form.get('comments', '')
                }
                
                update_vehicle_2(db, id, **vehicle_data)
                flash('Véhicule mis à jour avec succès!', 'success')
                return redirect(url_for('index_2'))
            except KeyError as e:
                logger.error(f"Missing form field in edit_vehicle_2: {str(e)}")
                flash('Tous les champs requis doivent être remplis.', 'danger')
            except ValueError as e:
                logger.error(f"Invalid value in edit_vehicle_2: {str(e)}")
                flash('Certaines valeurs sont invalides. Vérifiez les champs numériques et les dates.', 'danger')
            except Exception as e:
                logger.error(f"Error in edit_vehicle_2: {str(e)}")
                flash('Une erreur est survenue lors de la mise à jour du véhicule.', 'danger')
        
        return render_template('edit_vehicle_2.html', vehicle=vehicle)
    except Exception as e:
        logger.error(f"Error loading vehicle in edit_vehicle_2: {str(e)}")
        flash('Une erreur est survenue lors du chargement du véhicule.', 'danger')
        return redirect(url_for('index_2'))


@app.route('/delete_vehicle_1/<int:id>', methods=['POST'])
def delete_vehicle_1(id):
    try:
        db = next(get_db_1())
        if delete_vehicle_1(db, id):
            flash('Véhicule supprimé avec succès!', 'success')
        else:
            flash('Véhicule non trouvé.', 'danger')
    except Exception as e:
        logger.error(f"Error in delete_vehicle_1: {str(e)}")
        flash('Une erreur est survenue lors de la suppression du véhicule.', 'danger')
    return redirect(url_for('index_1'))

@app.route('/delete_vehicle_2/<int:id>', methods=['POST'])
def delete_vehicle_2(id):
    try:
        db = next(get_db_2())
        if delete_vehicle_2(db, id):
            flash('Véhicule supprimé avec succès!', 'success')
        else:
            flash('Véhicule non trouvé.', 'danger')
    except Exception as e:
        logger.error(f"Error in delete_vehicle_2: {str(e)}")
        flash('Une erreur est survenue lors de la suppression du véhicule.', 'danger')
    return redirect(url_for('index_2'))







# Initialize all databases and create ASGI app
try:
    init_db_1()
    init_db_2()
    
    from fastapi import FastAPI
    from fastapi.middleware.wsgi import WSGIMiddleware

    asgi_app = FastAPI()
    asgi_app.mount("/", WSGIMiddleware(app))

except Exception as e:
    logger.error(f"Error starting application: {str(e)}")
    raise e

if __name__ == '__main__':
    app.run(debug=True)
