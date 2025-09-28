from flask import Flask, render_template, request, redirect, url_for, flash
from crud import (
    create_collaborateur,
    get_collaborateur,
    get_collaborateurs,
    update_collaborateur,
    delete_collaborateur,
)
from database import get_db
from models import Collaborateur
from config import Config
from datetime import datetime

app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.config.from_object(Config)


# Define a custom filter to format dates
@app.template_filter("format_date")
def format_date(date):
    if date:
        return date.strftime("%d/%m/%Y")
    return ""


@app.route("/")
def index():
    return redirect(url_for("home"))


@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/collaborateurs")
def index_collaborateurs():
    db = next(get_db())
    search_term = request.args.get("search", "")
    collaborateurs = get_collaborateurs(db, search=search_term)
    return render_template(
        "collaborateurs.html", collaborateurs=collaborateurs, search_term=search_term
    )


@app.route("/collaborateurs/add", methods=["GET", "POST"])
def add_collaborateur():
    if request.method == "POST":
        try:
            db = next(get_db())
            new_collaborateur = Collaborateur(
                nom=request.form["nom"],
                prenom=request.form["prenom"],
                ifo=(
                    datetime.strptime(request.form["ifo"], "%Y-%m-%d").date()
                    if request.form.get("ifo")
                    else None
                ),
                caces=(
                    datetime.strptime(request.form["caces"], "%Y-%m-%d").date()
                    if request.form.get("caces")
                    else None
                ),
                airr=(
                    datetime.strptime(request.form["airr"], "%Y-%m-%d").date()
                    if request.form.get("airr")
                    else None
                ),
                hgo=(
                    datetime.strptime(request.form["hgo"], "%Y-%m-%d").date()
                    if request.form.get("hgo")
                    else None
                ),
                bo=(
                    datetime.strptime(request.form["bo"], "%Y-%m-%d").date()
                    if request.form.get("bo")
                    else None
                ),
                visite_med=(
                    datetime.strptime(request.form["visite_med"], "%Y-%m-%d").date()
                    if request.form.get("visite_med")
                    else None
                ),
                brevet_secour=(
                    datetime.strptime(request.form["brevet_secour"], "%Y-%m-%d").date()
                    if request.form.get("brevet_secour")
                    else None
                ),
                commentaire=request.form["commentaire"],
            )
            create_collaborateur(db, new_collaborateur)
            flash("Collaborateur ajouté avec succès!", "success")
            return redirect(url_for("index_collaborateurs"))
        except Exception as e:
            flash(f"Erreur lors de l'ajout du collaborateur: {str(e)}", "error")
            return redirect(url_for("add_collaborateur"))
    return render_template("add_collaborateur.html")


@app.route("/collaborateurs/edit/<int:id>", methods=["GET", "POST"])
def edit_collaborateur(id):
    db = next(get_db())
    collaborateur = get_collaborateur(db, id)
    if request.method == "POST":
        try:
            updates = {}
            for key, value in request.form.items():
                if value:
                    if key in [
                        "ifo",
                        "caces",
                        "airr",
                        "hgo",
                        "bo",
                        "visite_med",
                        "brevet_secour",
                    ]:
                        updates[key] = datetime.strptime(value, "%Y-%m-%d").date()
                    else:
                        updates[key] = value
                else:
                    updates[key] = None

            update_collaborateur(db, id, updates=updates)
            flash("Collaborateur mis à jour avec succès!", "success")
            return redirect(url_for("index_collaborateurs"))
        except Exception as e:
            flash(f"Erreur lors de la mise à jour du collaborateur: {str(e)}", "error")
            return redirect(url_for("edit_collaborateur", id=id))
    return render_template("edit_collaborateur.html", collaborateur=collaborateur)


@app.route("/collaborateurs/delete/<int:id>")
def delete_collaborateur_route(id):
    db = next(get_db())
    if delete_collaborateur(db, id):
        flash("Collaborateur supprimé avec succès!", "success")
    else:
        flash("Erreur lors de la suppression du collaborateur.", "error")
    return redirect(url_for("index_collaborateurs"))


if __name__ == "__main__":
    app.run(debug=False, port=5003)
