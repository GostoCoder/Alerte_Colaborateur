from flask import Flask, render_template, request, redirect, url_for, flash
from crud_2 import get_vehicles_2, get_vehicle_2, create_vehicle_2, update_vehicle_2, delete_vehicle_2
from crud_1 import get_collaborateurs as get_collaborateurs_1, get_collaborateur as get_collaborateur_1, create_collaborateur as create_collaborateur_1, update_collaborateur as update_collaborateur_1, delete_collaborateur as delete_collaborateur_1
from database_2 import get_db as get_db_2
from database_1 import get_db as get_db_1
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

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
    collaborateurs = get_collaborateurs_1(db, search=search_term)
    return render_template('index_1.html',
                         collaborateurs=collaborateurs,
                         search_term=search_term)

@app.route('/index_2')
def index_2():
    db = next(get_db_2())
    search_term = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'brand')
    sort_order = request.args.get('sort_order', 'asc')
    allowed_sort_fields = ['vehicle_type', 'brand', 'commercial_type', 'group_number',
                          'license_plate', 'limit_periodic_inspection', 'kilometer_periodic_inspection',
                          'limit_additional_inspection', 'kilometer_additional_inspection',
                          'date_periodic_inspection', 'date_additional_inspection']
    if sort_by not in allowed_sort_fields:
        sort_by = 'brand'
    vehicles = get_vehicles_2(db, search=search_term, sort_by=sort_by, direction=sort_order)
    return render_template('index_2.html',
                         vehicles=vehicles,
                         search_term=search_term,
                         sort_by=sort_by,
                         sort_order=sort_order)

@app.route('/add_vehicle_1', methods=['GET', 'POST'])
def add_vehicle_1():
    if request.method == 'POST':
        try:
            nom = request.form['nom']
            prenom = request.form['prenom']
            fimo = request.form.get('fimo')
            caces = request.form.get('caces')
            aipr = request.form.get('aipr')
            hg0b0 = request.form.get('hg0b0')
            visite_med = request.form.get('visite_med')
            brevet_secour = request.form.get('brevet_secour')
            commentaire = request.form.get('commentaire')
            db = next(get_db_1())
            create_collaborateur_1(
                db,
                nom=nom,
                prenom=prenom,
                fimo=fimo,
                caces=caces,
                aipr=aipr,
                hg0b0=hg0b0,
                visite_med=visite_med,
                brevet_secour=brevet_secour,
                commentaire=commentaire
            )
            flash('Collaborateur ajouté avec succès!', 'success')
            return redirect(url_for('index_1'))
        except Exception as e:
            flash(f'Erreur lors de l\'ajout du collaborateur: {str(e)}', 'error')
            return redirect(url_for('add_vehicle_1'))
    return render_template('add_collaborateur_1.html')

@app.route('/add_vehicle_2', methods=['GET', 'POST'])
def add_vehicle_2():
    if request.method == 'POST':
        try:
            vehicle_type = request.form['vehicle_type']
            brand = request.form['brand']
            commercial_type = request.form['commercial_type']
            group_number = request.form.get('group_number', type=int)
            license_plate = request.form['license_plate']
            work_with = request.form.get('work_with') or None
            kilometer_additional_inspection = request.form.get('kilometer_additional_inspection', type=int)
            def parse_dt(field):
                val = request.form.get(field)
                return datetime.strptime(val, '%Y-%m-%d') if val else None
            ct_soeco_date = parse_dt('ct_soeco_date')
            euromaster_chrono = parse_dt('euromaster_chrono')
            euromaster_limiteur = parse_dt('euromaster_limiteur')
            ned92_chrono = parse_dt('ned92_chrono')
            ned92_limiteur = parse_dt('ned92_limiteur')
            date_technical_inspection = parse_dt('date_technical_inspection')
            date_chrono = parse_dt('date_chrono')
            date_limiteur = parse_dt('date_limiteur')
            comments = request.form.get('comments') or None
            db = next(get_db_2())
            create_vehicle_2(db,
                           vehicle_type=vehicle_type,
                           brand=brand,
                           commercial_type=commercial_type,
                           group_number=group_number,
                           license_plate=license_plate,
                           work_with=work_with,
                           kilometer_additional_inspection=kilometer_additional_inspection,
                           ct_soeco_date=ct_soeco_date,
                           euromaster_chrono=euromaster_chrono,
                           euromaster_limiteur=euromaster_limiteur,
                           ned92_chrono=ned92_chrono,
                           ned92_limiteur=ned92_limiteur,
                           date_technical_inspection=date_technical_inspection,
                           date_chrono=date_chrono,
                           date_limiteur=date_limiteur,
                           comments=comments)
            flash('Véhicule ajouté avec succès!', 'success')
            return redirect(url_for('index_2'))
        except ValueError as e:
            flash(f'Erreur de format de date: {str(e)}', 'error')
            return redirect(url_for('add_vehicle_2'))
        except Exception as e:
            flash(f'Erreur lors de l\'ajout du véhicule: {str(e)}', 'error')
            return redirect(url_for('add_vehicle_2'))
    return render_template('add_vehicle_2.html')

@app.route('/edit_vehicle_1/<int:id>', methods=['GET', 'POST'])
def edit_vehicle_1(id):
    db = next(get_db_1())
    collaborateur = get_collaborateur_1(db, id)
    if request.method == 'POST':
        try:
            nom = request.form.get('nom')
            prenom = request.form.get('prenom')
            fimo = request.form.get('fimo')
            caces = request.form.get('caces')
            aipr = request.form.get('aipr')
            hg0b0 = request.form.get('hg0b0')
            visite_med = request.form.get('visite_med')
            brevet_secour = request.form.get('brevet_secour')
            commentaire = request.form.get('commentaire')
            update_collaborateur_1(
                db,
                id,
                nom=nom,
                prenom=prenom,
                fimo=fimo,
                caces=caces,
                aipr=aipr,
                hg0b0=hg0b0,
                visite_med=visite_med,
                brevet_secour=brevet_secour,
                commentaire=commentaire
            )
            flash('Collaborateur mis à jour avec succès!', 'success')
            return redirect(url_for('index_1'))
        except Exception as e:
            flash(f'Erreur lors de la mise à jour du collaborateur: {str(e)}', 'error')
            return redirect(url_for('edit_vehicle_1', id=id))
    return render_template('edit_collaborateur_1.html', collaborateur=collaborateur)

@app.route('/edit_vehicle_2/<int:id>', methods=['GET', 'POST'])
def edit_vehicle_2(id):
    db = next(get_db_2())
    vehicle = get_vehicle_2(db, id)
    if request.method == 'POST':
        try:
            vehicle_type = request.form['vehicle_type']
            brand = request.form['brand']
            commercial_type = request.form['commercial_type']
            group_number = request.form.get('group_number', type=int)
            license_plate = request.form['license_plate']
            work_with = request.form.get('work_with') or None
            kilometer_additional_inspection = request.form.get('kilometer_additional_inspection', type=int)
            def parse_dt(field):
                val = request.form.get(field)
                return datetime.strptime(val, '%Y-%m-%d') if val else None
            ct_soeco_date = parse_dt('ct_soeco_date')
            euromaster_chrono = parse_dt('euromaster_chrono')
            euromaster_limiteur = parse_dt('euromaster_limiteur')
            ned92_chrono = parse_dt('ned92_chrono')
            ned92_limiteur = parse_dt('ned92_limiteur')
            date_technical_inspection = parse_dt('date_technical_inspection')
            date_chrono = parse_dt('date_chrono')
            date_limiteur = parse_dt('date_limiteur')
            comments = request.form.get('comments') or None
            update_vehicle_2(db, id,
                           vehicle_type=vehicle_type,
                           brand=brand,
                           commercial_type=commercial_type,
                           group_number=group_number,
                           license_plate=license_plate,
                           work_with=work_with,
                           kilometer_additional_inspection=kilometer_additional_inspection,
                           ct_soeco_date=ct_soeco_date,
                           euromaster_chrono=euromaster_chrono,
                           euromaster_limiteur=euromaster_limiteur,
                           ned92_chrono=ned92_chrono,
                           ned92_limiteur=ned92_limiteur,
                           date_technical_inspection=date_technical_inspection,
                           date_chrono=date_chrono,
                           date_limiteur=date_limiteur,
                           comments=comments)
            flash('Véhicule modifié avec succès!', 'success')
            return redirect(url_for('index_2'))
        except ValueError as e:
            flash(f'Erreur de format de date: {str(e)}', 'error')
            return redirect(url_for('edit_vehicle_2', id=id))
        except Exception as e:
            flash(f'Erreur lors de la modification du véhicule: {str(e)}', 'error')
            return redirect(url_for('edit_vehicle_2', id=id))
    if vehicle is None:
        flash('Véhicule non trouvé.', 'error')
        return redirect(url_for('index_2'))
    return render_template('edit_vehicle_2.html', vehicle=vehicle)

@app.route('/delete_vehicle_1/<int:id>')
def delete_vehicle_route_1(id):
    db = next(get_db_1())
    if delete_collaborateur_1(db, id):
        flash('Collaborateur supprimé avec succès!', 'success')
    else:
        flash('Erreur lors de la suppression du collaborateur.', 'error')
    return redirect(url_for('index_1'))

@app.route('/delete_vehicle_2/<int:id>')
def delete_vehicle_route_2(id):
    db = next(get_db_2())
    delete_vehicle_2(db, id)
    return redirect(url_for('index_2'))

if __name__ == '__main__':
    app.run(debug=False, port=5003)
