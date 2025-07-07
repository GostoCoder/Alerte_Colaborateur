from flask import Flask, render_template, request, redirect, url_for, flash
from crud_1 import create_collaborateur, get_collaborateur, get_collaborateurs, update_collaborateur, delete_collaborateur
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
    collaborateurs = get_collaborateurs(db, search=search_term)
    return render_template('index_1.html', 
                         vehicles=collaborateurs, 
                         search_term=search_term)

@app.route('/add_vehicle_1', methods=['GET', 'POST'])
def add_vehicle_1():
    if request.method == 'POST':
        try:
            nom = request.form['nom']
            prenom = request.form['prenom']
            ifo = request.form['ifo'] or None
            caces = request.form['caces'] or None
            airr = request.form['airr'] or None
            hgo = request.form['hgo'] or None
            bo = request.form['bo'] or None
            visite_med = request.form['visite_med'] or None
            brevet_secour = request.form['brevet_secour'] or None
            commentaire = request.form['commentaire']

            db = next(get_db_1())
            create_collaborateur(
                db,
                nom=nom,
                prenom=prenom,
                ifo=datetime.strptime(ifo, '%Y-%m-%d') if ifo else None,
                caces=datetime.strptime(caces, '%Y-%m-%d') if caces else None,
                airr=datetime.strptime(airr, '%Y-%m-%d') if airr else None,
                hgo=datetime.strptime(hgo, '%Y-%m-%d') if hgo else None,
                bo=datetime.strptime(bo, '%Y-%m-%d') if bo else None,
                visite_med=datetime.strptime(visite_med, '%Y-%m-%d') if visite_med else None,
                brevet_secour=datetime.strptime(brevet_secour, '%Y-%m-%d') if brevet_secour else None,
                commentaire=commentaire
            )
            flash('Collaborateur ajouté avec succès!', 'success')
            return redirect(url_for('index_1'))
        except Exception as e:
            flash(f'Erreur lors de l\'ajout du collaborateur: {str(e)}', 'error')
            return redirect(url_for('add_vehicle_1'))
    return render_template('add_vehicle_1.html')

@app.route('/edit_vehicle_1/<int:id>', methods=['GET', 'POST'])
def edit_vehicle_1(id):
    db = next(get_db_1())
    collaborateur = get_collaborateur(db, id)
    if request.method == 'POST':
        try:
            nom = request.form['nom']
            prenom = request.form['prenom']
            ifo = request.form['ifo'] or None
            caces = request.form['caces'] or None
            airr = request.form['airr'] or None
            hgo = request.form['hgo'] or None
            bo = request.form['bo'] or None
            visite_med = request.form['visite_med'] or None
            brevet_secour = request.form['brevet_secour'] or None
            commentaire = request.form['commentaire']

            update_collaborateur(
                db,
                id,
                nom=nom,
                prenom=prenom,
                ifo=datetime.strptime(ifo, '%Y-%m-%d') if ifo else None,
                caces=datetime.strptime(caces, '%Y-%m-%d') if caces else None,
                airr=datetime.strptime(airr, '%Y-%m-%d') if airr else None,
                hgo=datetime.strptime(hgo, '%Y-%m-%d') if hgo else None,
                bo=datetime.strptime(bo, '%Y-%m-%d') if bo else None,
                visite_med=datetime.strptime(visite_med, '%Y-%m-%d') if visite_med else None,
                brevet_secour=datetime.strptime(brevet_secour, '%Y-%m-%d') if brevet_secour else None,
                commentaire=commentaire
            )
            flash('Collaborateur mis à jour avec succès!', 'success')
            return redirect(url_for('index_1'))
        except Exception as e:
            flash(f'Erreur lors de la mise à jour du collaborateur: {str(e)}', 'error')
            return redirect(url_for('edit_vehicle_1', id=id))
    return render_template('edit_vehicle_1.html', collaborateur=collaborateur)


@app.route('/delete_vehicle_1/<int:id>')
def delete_vehicle_route_1(id):
    db = next(get_db_1())
    if delete_collaborateur(db, id):
        flash('Collaborateur supprimé avec succès!', 'success')
    else:
        flash('Erreur lors de la suppression du collaborateur.', 'error')
    return redirect(url_for('index_1'))

if __name__ == '__main__':
    app.run(debug=False, port=5003)
