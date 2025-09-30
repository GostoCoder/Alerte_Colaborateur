from flask import Flask, render_template, request, redirect, url_for, flash
from database_1 import get_db as get_db_1, init_db as init_db_1
from database_2 import get_db as get_db_2, init_db as init_db_2

from crud_1 import (
    get_collaborateurs as get_collaborateurs_1,
    create_collaborateur as create_collaborateur_1,
    get_collaborateur as get_collaborateur_1,
    delete_collaborateur as delete_collaborateur_1,
    update_collaborateur as update_collaborateur_1
)
from crud_2 import (
    get_collaborateurs_2,
    create_collaborateur_2,
    get_collaborateur_2,
    delete_collaborateur_2,
    update_collaborateur_2
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
        sort_by = request.args.get('sort_by', 'nom')
        sort_order = request.args.get('sort_order', 'asc')
        collaborateurs = get_collaborateurs_1(db, 0, 100, search_term)
        return render_template('index_1.html', collaborateurs=collaborateurs, search_term=search_term,
                             sort_by=sort_by, sort_order=sort_order)
    except Exception as e:
        logger.error(f"Error in index_1: {str(e)}")
        flash('Une erreur est survenue lors du chargement des collaborateurs.', 'danger')
        return render_template('index_1.html', collaborateurs=[], search_term='',
                             sort_by='nom', sort_order='asc')

@app.route('/index_2')
def index_2():
    try:
        db = next(get_db_2())
        search_term = request.args.get('search', '')
        sort_by = request.args.get('sort_by', 'nom')
        sort_order = request.args.get('sort_order', 'asc')
        
        collaborateurs = get_collaborateurs_2(db, 0, 100, search_term, sort_by, sort_order)
        return render_template('index_2.html', collaborateurs=collaborateurs, search_term=search_term,
                             sort_by=sort_by, sort_order=sort_order)
    except Exception as e:
        logger.error(f"Error in index_2: {str(e)}")
        flash('Une erreur est survenue lors du chargement des collaborateurs.', 'danger')
        return render_template('index_2.html', collaborateurs=[], search_term='',
                             sort_by='nom', sort_order='asc')


@app.route('/add_collaborateur_1', methods=['GET', 'POST'])
def add_collaborateur_1():
    if request.method == 'POST':
        try:
            db = next(get_db_1())
            collab_data = {
                'nom': request.form['nom'],
                'prenom': request.form['prenom'],
                'fimo': request.form['fimo'] if request.form['fimo'] else None,
                'caces': request.form['caces'] if request.form['caces'] else None,
                'aipr': request.form['aipr'] if request.form['aipr'] else None,
                'hg0b0': request.form['hg0b0'] if request.form['hg0b0'] else None,
                'visite_med': request.form['visite_med'] if request.form['visite_med'] else None,
                'brevet_secour': request.form['brevet_secour'] if request.form['brevet_secour'] else None,
                'commentaire': request.form.get('commentaire', '')
            }
            create_collaborateur_1(db, **collab_data)
            flash('Collaborateur ajouté avec succès!', 'success')
            return redirect(url_for('index_1'))
        except KeyError as e:
            logger.error(f"Missing form field in add_collaborateur_1: {str(e)}")
            flash('Tous les champs requis doivent être remplis.', 'danger')
        except ValueError as e:
            logger.error(f"Invalid value in add_collaborateur_1: {str(e)}")
            flash('Certaines valeurs sont invalides. Vérifiez les champs et les dates.', 'danger')
        except Exception as e:
            logger.error(f"Error in add_collaborateur_1: {str(e)}")
            flash('Une erreur est survenue lors de l\'ajout du collaborateur.', 'danger')
    return render_template('add_collaborateur_1.html')

@app.route('/add_collaborateur_2', methods=['GET', 'POST'])
def add_collaborateur_2():
    if request.method == 'POST':
        try:
            db = next(get_db_2())
            collab_data = {
                'nom': request.form['nom'],
                'prenom': request.form['prenom'],
                'date_renouvellement': datetime.strptime(request.form['date_renouvellement'], '%Y-%m-%d').date() if request.form['date_renouvellement'] else None,
                'date_validite': datetime.strptime(request.form['date_validite'], '%Y-%m-%d').date() if request.form['date_validite'] else None,
                'commentaire': request.form.get('commentaire', '')
            }
            create_collaborateur_2(db, **collab_data)
            flash('Collaborateur ajouté avec succès!', 'success')
            return redirect(url_for('index_2'))
        except KeyError as e:
            logger.error(f"Missing form field in add_collaborateur_2: {str(e)}")
            flash('Tous les champs requis doivent être remplis.', 'danger')
        except ValueError as e:
            logger.error(f"Invalid value in add_collaborateur_2: {str(e)}")
            flash('Certaines valeurs sont invalides. Vérifiez les champs et les dates.', 'danger')
        except Exception as e:
            logger.error(f"Error in add_collaborateur_2: {str(e)}")
            flash('Une erreur est survenue lors de l\'ajout du collaborateur.', 'danger')
    return render_template('add_collaborateur_2.html')

@app.route('/edit_collaborateur_1/<int:id>', methods=['GET', 'POST'])
def edit_collaborateur_1(id):
    try:
        db = next(get_db_1())
        collaborateur = get_collaborateur_1(db, id)
        if not collaborateur:
            flash('Collaborateur non trouvé.', 'danger')
            return redirect(url_for('index_1'))
        if request.method == 'POST':
            try:
                collab_data = {
                    'nom': request.form['nom'],
                    'prenom': request.form['prenom'],
                    'fimo': request.form['fimo'] if request.form['fimo'] else None,
                    'caces': request.form['caces'] if request.form['caces'] else None,
                    'aipr': request.form['aipr'] if request.form['aipr'] else None,
                    'hg0b0': request.form['hg0b0'] if request.form['hg0b0'] else None,
                    'visite_med': request.form['visite_med'] if request.form['visite_med'] else None,
                    'brevet_secour': request.form['brevet_secour'] if request.form['brevet_secour'] else None,
                    'commentaire': request.form.get('commentaire', '')
                }
                update_collaborateur_1(db, id, **collab_data)
                flash('Collaborateur mis à jour avec succès!', 'success')
                return redirect(url_for('index_1'))
            except KeyError as e:
                logger.error(f"Missing form field in edit_collaborateur_1: {str(e)}")
                flash('Tous les champs requis doivent être remplis.', 'danger')
            except ValueError as e:
                logger.error(f"Invalid value in edit_collaborateur_1: {str(e)}")
                flash('Certaines valeurs sont invalides. Vérifiez les champs et les dates.', 'danger')
            except Exception as e:
                logger.error(f"Error in edit_collaborateur_1: {str(e)}")
                flash('Une erreur est survenue lors de la mise à jour du collaborateur.', 'danger')
        return render_template('edit_collaborateur_1.html', collaborateur=collaborateur)
    except Exception as e:
        logger.error(f"Error loading collaborateur in edit_collaborateur_1: {str(e)}")
        flash('Une erreur est survenue lors du chargement du collaborateur.', 'danger')
        return redirect(url_for('index_1'))

@app.route('/edit_collaborateur_2/<int:id>', methods=['GET', 'POST'])
def edit_collaborateur_2(id):
    try:
        db = next(get_db_2())
        collaborateur = get_collaborateur_2(db, id)
        if not collaborateur:
            flash('Collaborateur non trouvé.', 'danger')
            return redirect(url_for('index_2'))
        if request.method == 'POST':
            try:
                collab_data = {
                    'nom': request.form['nom'],
                    'prenom': request.form['prenom'],
                    'date_renouvellement': datetime.strptime(request.form['date_renouvellement'], '%Y-%m-%d').date() if request.form['date_renouvellement'] else None,
                    'date_validite': datetime.strptime(request.form['date_validite'], '%Y-%m-%d').date() if request.form['date_validite'] else None,
                    'commentaire': request.form.get('commentaire', '')
                }
                update_collaborateur_2(db, id, **collab_data)
                flash('Collaborateur mis à jour avec succès!', 'success')
                return redirect(url_for('index_2'))
            except KeyError as e:
                logger.error(f"Missing form field in edit_collaborateur_2: {str(e)}")
                flash('Tous les champs requis doivent être remplis.', 'danger')
            except ValueError as e:
                logger.error(f"Invalid value in edit_collaborateur_2: {str(e)}")
                flash('Certaines valeurs sont invalides. Vérifiez les champs et les dates.', 'danger')
            except Exception as e:
                logger.error(f"Error in edit_collaborateur_2: {str(e)}")
                flash('Une erreur est survenue lors de la mise à jour du collaborateur.', 'danger')
        return render_template('edit_collaborateur_2.html', collaborateur=collaborateur)
    except Exception as e:
        logger.error(f"Error loading collaborateur in edit_collaborateur_2: {str(e)}")
        flash('Une erreur est survenue lors du chargement du collaborateur.', 'danger')
        return redirect(url_for('index_2'))


@app.route('/delete_collaborateur_1/<int:id>', methods=['POST'])
def delete_collaborateur_1_route(id):
    try:
        db = next(get_db_1())
        if delete_collaborateur_1(db, id):
            flash('Collaborateur supprimé avec succès!', 'success')
        else:
            flash('Collaborateur non trouvé.', 'danger')
    except Exception as e:
        logger.error(f"Error in delete_collaborateur_1: {str(e)}")
        flash('Une erreur est survenue lors de la suppression du collaborateur.', 'danger')
    return redirect(url_for('index_1'))

@app.route('/delete_collaborateur_2/<int:id>', methods=['POST'])
def delete_collaborateur_2_route(id):
    try:
        db = next(get_db_2())
        if delete_collaborateur_2(db, id):
            flash('Collaborateur supprimé avec succès!', 'success')
        else:
            flash('Collaborateur non trouvé.', 'danger')
    except Exception as e:
        logger.error(f"Error in delete_collaborateur_2: {str(e)}")
        flash('Une erreur est survenue lors de la suppression du collaborateur.', 'danger')
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
