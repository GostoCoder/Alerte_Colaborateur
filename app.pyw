from flask import Flask, render_template, request, redirect, url_for, flash
from crud_2 import get_collaborateurs_2, get_collaborateur_2, create_collaborateur_2, update_collaborateur_2, delete_collaborateur_2
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
        return date.strftime('%Y-%m-%d')
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
    allowed_sort_fields = ['nom', 'prenom', 'date_renouvellement', 'date_validite']
    if sort_by not in allowed_sort_fields:
        sort_by = 'nom'
    collaborateurs = get_collaborateurs_2(db, search=search_term, sort_by=sort_by, direction=sort_order)
    return render_template('index_2.html',
                         collaborateurs=collaborateurs,
                         search_term=search_term,
                         sort_by=sort_by,
                         sort_order=sort_order)

@app.route('/add_collaborateur_1', methods=['GET', 'POST'])
def add_collaborateur_1():
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
            return redirect(url_for('add_collaborateur_1'))
    return render_template('add_collaborateur_1.html')

@app.route('/add_collaborateur_2', methods=['GET', 'POST'])
def add_collaborateur_2():
    if request.method == 'POST':
        try:
            nom = request.form['nom']
            prenom = request.form['prenom']
            date_renouvellement_str = request.form.get('date_renouvellement')
            date_validite_str = request.form.get('date_validite')
            commentaire = request.form.get('commentaire')
            from datetime import datetime
            date_renouvellement = datetime.strptime(date_renouvellement_str, '%Y-%m-%d').date() if date_renouvellement_str else None
            date_validite = datetime.strptime(date_validite_str, '%Y-%m-%d').date() if date_validite_str else None
            db = next(get_db_2())
            create_collaborateur_2(
                db,
                nom=nom,
                prenom=prenom,
                date_renouvellement=date_renouvellement,
                date_validite=date_validite,
                commentaire=commentaire
            )
            flash('Collaborateur ajouté avec succès!', 'success')
            return redirect(url_for('index_2'))
        except Exception as e:
            flash(f'Erreur lors de l\'ajout du collaborateur: {str(e)}', 'error')
            return redirect(url_for('add_collaborateur_2'))
    return render_template('add_collaborateur_2.html')

@app.route('/edit_collaborateur_1/<int:id>', methods=['GET', 'POST'])
def edit_collaborateur_1(id):
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
            return redirect(url_for('edit_collaborateur_1', id=id))
    return render_template('edit_collaborateur_1.html', collaborateur=collaborateur)

@app.route('/edit_collaborateur_2/<int:id>', methods=['GET', 'POST'])
def edit_collaborateur_2(id):
    db = next(get_db_2())
    collaborateur = get_collaborateur_2(db, id)
    if request.method == 'POST':
        try:
            nom = request.form.get('nom')
            prenom = request.form.get('prenom')
            date_renouvellement_str = request.form.get('date_renouvellement')
            date_validite_str = request.form.get('date_validite')
            commentaire = request.form.get('commentaire')
            from datetime import datetime
            date_renouvellement = datetime.strptime(date_renouvellement_str, '%Y-%m-%d').date() if date_renouvellement_str else None
            date_validite = datetime.strptime(date_validite_str, '%Y-%m-%d').date() if date_validite_str else None
            update_collaborateur_2(
                db,
                id,
                nom=nom,
                prenom=prenom,
                date_renouvellement=date_renouvellement,
                date_validite=date_validite,
                commentaire=commentaire
            )
            flash('Collaborateur mis à jour avec succès!', 'success')
            return redirect(url_for('index_2'))
        except Exception as e:
            flash(f'Erreur lors de la mise à jour du collaborateur: {str(e)}', 'error')
            return redirect(url_for('edit_collaborateur_2', id=id))
    if collaborateur is None:
        flash('Collaborateur non trouvé.', 'error')
        return redirect(url_for('index_2'))
    return render_template('edit_collaborateur_2.html', collaborateur=collaborateur)

@app.route('/delete_collaborateur_route_1/<int:id>')
def delete_collaborateur_route_1(id):
    db = next(get_db_1())
    if delete_collaborateur_1(db, id):
        flash('Collaborateur supprimé avec succès!', 'success')
    else:
        flash('Erreur lors de la suppression du collaborateur.', 'error')
    return redirect(url_for('index_1'))

@app.route('/delete_collaborateur_route_2/<int:id>')
def delete_collaborateur_route_2(id):
    db = next(get_db_2())
    delete_collaborateur_2(db, id)
    return redirect(url_for('index_2'))

if __name__ == '__main__':
    app.run(debug=False, port=5003)
