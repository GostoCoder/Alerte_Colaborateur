import pandas as pd
import sqlite3
from datetime import datetime, date
import os
import re
from typing import Optional, Dict, List
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CollaborateurSeeder:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.collaborateurs_data = {}

    def normalize_name(self, name: str) -> tuple:
        """Normalize and split names for consistent matching"""
        if not name or pd.isna(name):
            return None, None

        name = str(name).strip().upper()

        # Handle cases like "DA SILVA GONCALVES JOSE"
        parts = name.split()
        if len(parts) >= 2:
            # Last part is usually the first name
            prenom = parts[-1]
            # Everything else is the last name
            nom = " ".join(parts[:-1])
            return nom, prenom
        return name, None

    def parse_date(self, date_str) -> Optional[date]:
        """Parse various date formats to standard date object"""
        if (
            not date_str
            or pd.isna(date_str)
            or str(date_str).strip() == ""
            or str(date_str).upper() in ["A PASSER", "DISPENSÉ", "ABSENT"]
        ):
            return None

        date_str = str(date_str).strip()

        # Try different date formats
        formats = [
            "%d/%m/%Y",
            "%d/%m/%y",
            "%m/%d/%y",
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d-%m-%Y",
        ]

        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                # If year is less than 50, assume it's 20xx, otherwise 19xx
                if fmt in ["%d/%m/%y", "%m/%d/%y"] and parsed_date.year < 1950:
                    parsed_date = parsed_date.replace(year=parsed_date.year + 100)
                return parsed_date.date()
            except ValueError:
                continue

        logger.warning(f"Could not parse date: {date_str}")
        return None

    def load_apst_data(self):
        """Load personnel data from APST file"""
        logger.info("Loading APST personnel data...")
        try:
            # Read the file as text first to handle the format properly
            with open("APST - FICHIER DU PERSONNEL...csv", "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Skip header lines and process data
            for line in lines[3:]:  # Skip first 3 lines
                parts = line.strip().split()
                if len(parts) >= 2:
                    # Extract name parts - usually nom, prenom, and optionally date
                    nom = parts[0]
                    prenom = parts[1]

                    # Look for date (format like 20/02/2025)
                    visite_med = None
                    date_pattern = r"\d{1,2}/\d{1,2}/\d{4}"
                    date_matches = re.findall(date_pattern, line)
                    if date_matches:
                        visite_med = self.parse_date(date_matches[0])

                    nom, prenom_normalized = self.normalize_name(f"{nom} {prenom}")

                    if nom:
                        key = f"{nom}_{prenom_normalized}" if prenom_normalized else nom

                        self.collaborateurs_data[key] = {
                            "nom": nom,
                            "prenom": prenom_normalized or prenom,
                            "visite_med": visite_med,
                            "ifo": None,
                            "caces": None,
                            "airr": None,
                            "hgo": None,
                            "bo": None,
                            "brevet_secour": None,
                            "commentaire": None,
                        }

            logger.info(
                f"Loaded {len(self.collaborateurs_data)} personnel records from APST"
            )

        except Exception as e:
            logger.error(f"Error loading APST data: {e}")

    def load_secouriste_data(self):
        """Load first aid certification data"""
        logger.info("Loading Secouriste data...")
        try:
            df = pd.read_csv("SECOURISTE EN COURS.csv", sep=";", skiprows=10)

            for _, row in df.iterrows():
                if pd.notna(row.iloc[0]) and str(row.iloc[0]).strip():
                    name = str(row.iloc[0]).strip()
                    nom, prenom = self.normalize_name(name)

                    if nom:
                        key = f"{nom}_{prenom}" if prenom else nom

                        # Get certification date
                        brevet_secour = None
                        if len(row) > 2 and pd.notna(row.iloc[2]):
                            brevet_secour = self.parse_date(row.iloc[2])

                        # Update existing record or create new one
                        if key in self.collaborateurs_data:
                            self.collaborateurs_data[key][
                                "brevet_secour"
                            ] = brevet_secour
                        else:
                            self.collaborateurs_data[key] = {
                                "nom": nom,
                                "prenom": prenom,
                                "visite_med": None,
                                "ifo": None,
                                "caces": None,
                                "airr": None,
                                "hgo": None,
                                "bo": None,
                                "brevet_secour": brevet_secour,
                                "commentaire": None,
                            }

            logger.info("Loaded Secouriste certification data")

        except Exception as e:
            logger.error(f"Error loading Secouriste data: {e}")

    def load_caces_data(self):
        """Load CACES certification data from the complex CACES file"""
        logger.info("Loading CACES data...")
        try:
            # Read the file as text first to handle the complex format
            with open(
                "AAAAAAAAAAAAA -Tableau information et formation CACES - FIMO.csv",
                "r",
                encoding="utf-8",
            ) as f:
                content = f.read()

            # Extract employee data using regex patterns
            lines = content.split("\n")

            for line in lines:
                # Look for lines that start with employee names (more flexible pattern)
                if re.match(r"^[A-Z][A-Z\s]+ [A-Z]", line.strip()):
                    parts = line.split()
                    if len(parts) >= 2:
                        # Extract name (usually first two parts)
                        potential_nom = parts[0]
                        potential_prenom = parts[1]

                        nom, prenom = self.normalize_name(
                            f"{potential_nom} {potential_prenom}"
                        )

                        if nom:
                            key = f"{nom}_{prenom}" if prenom else nom

                            # Try to extract birth date (which might be mistakenly parsed as CACES date)
                            # Look for date patterns (dd/mm/yyyy) - birth date is usually the first date
                            date_pattern = r"(\d{1,2}/\d{1,2}/\d{4})"
                            dates = re.findall(date_pattern, line)

                            # Update existing record or create new one
                            if key in self.collaborateurs_data:
                                # For existing records, try to find actual certification dates
                                # Skip the first date (likely birth date) and look for later dates
                                if (
                                    len(dates) > 3
                                ):  # If multiple dates, later ones might be certifications
                                    self.collaborateurs_data[key]["caces"] = (
                                        self.parse_date(dates[3])
                                    )
                                elif len(dates) > 1:
                                    self.collaborateurs_data[key]["caces"] = (
                                        self.parse_date(dates[1])
                                    )
                            else:
                                # For new records, be more conservative about dates
                                caces_date = None
                                if len(dates) > 3:
                                    caces_date = self.parse_date(dates[3])

                                self.collaborateurs_data[key] = {
                                    "nom": nom,
                                    "prenom": prenom,
                                    "visite_med": None,
                                    "ifo": None,
                                    "caces": caces_date,
                                    "airr": None,
                                    "hgo": None,
                                    "bo": None,
                                    "brevet_secour": None,
                                    "commentaire": (
                                        "CACES data available" if dates else None
                                    ),
                                }

            logger.info("Loaded CACES certification data")

        except Exception as e:
            logger.error(f"Error loading CACES data: {e}")

    def load_planning_data(self):
        """Load planning formations data"""
        logger.info("Loading Planning Formations data...")
        try:
            # Skip header rows and read the data
            df = pd.read_csv("PLANNING FORMATIONS.csv", skiprows=7)

            for _, row in df.iterrows():
                if (
                    pd.notna(row.iloc[0])
                    and str(row.iloc[0]).strip()
                    and len(str(row.iloc[0]).strip()) > 2
                ):
                    nom_raw = str(row.iloc[0]).strip()
                    prenom_raw = (
                        str(row.iloc[1]).strip()
                        if len(row) > 1 and pd.notna(row.iloc[1])
                        else ""
                    )

                    nom, prenom = self.normalize_name(f"{nom_raw} {prenom_raw}")

                    if nom:
                        key = f"{nom}_{prenom}" if prenom else nom

                        # Extract BO/HO dates (columns around index 4-5)
                        bo_date = None
                        if len(row) > 4 and pd.notna(row.iloc[4]):
                            bo_date = self.parse_date(row.iloc[4])

                        # Extract AIPR dates (columns around index 6-7)
                        airr_date = None
                        if len(row) > 6 and pd.notna(row.iloc[6]):
                            airr_date = self.parse_date(row.iloc[6])

                        # Update existing record or create new one
                        if key in self.collaborateurs_data:
                            if bo_date:
                                self.collaborateurs_data[key]["bo"] = bo_date
                            if airr_date:
                                self.collaborateurs_data[key]["airr"] = airr_date
                        else:
                            self.collaborateurs_data[key] = {
                                "nom": nom,
                                "prenom": prenom,
                                "visite_med": None,
                                "ifo": None,
                                "caces": None,
                                "airr": airr_date,
                                "hgo": None,
                                "bo": bo_date,
                                "brevet_secour": None,
                                "commentaire": None,
                            }

            logger.info("Loaded Planning Formations data")

        except Exception as e:
            logger.error(f"Error loading Planning data: {e}")

    def seed_database(self):
        """Seed the database with consolidated data"""
        logger.info("Seeding database...")

        try:
            # Connect to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Clear existing data
            cursor.execute("DELETE FROM collaborateurs")
            logger.info("Cleared existing collaborateurs data")

            # Insert consolidated data
            inserted_count = 0
            for key, data in self.collaborateurs_data.items():
                try:
                    cursor.execute(
                        """
                        INSERT INTO collaborateurs (
                            nom, prenom, ifo, caces, airr, hgo, bo, 
                            visite_med, brevet_secour, commentaire
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            data["nom"],
                            data["prenom"],
                            data["ifo"],
                            data["caces"],
                            data["airr"],
                            data["hgo"],
                            data["bo"],
                            data["visite_med"],
                            data["brevet_secour"],
                            data["commentaire"],
                        ),
                    )
                    inserted_count += 1
                except Exception as e:
                    logger.warning(f"Error inserting record for {key}: {e}")

            conn.commit()
            conn.close()

            logger.info(
                f"Successfully seeded database with {inserted_count} collaborateur records"
            )
            return inserted_count

        except Exception as e:
            logger.error(f"Error seeding database: {e}")
            raise

    def run_seeding(self):
        """Run the complete seeding process"""
        logger.info("Starting collaborateur seeding process...")

        # Load data from all CSV sources
        self.load_apst_data()
        self.load_secouriste_data()
        self.load_caces_data()
        self.load_planning_data()

        logger.info(
            f"Total unique collaborateurs consolidated: {len(self.collaborateurs_data)}"
        )

        # Print sample data for verification
        logger.info("Sample consolidated data:")
        for i, (key, data) in enumerate(self.collaborateurs_data.items()):
            if i < 3:  # Show first 3 records
                logger.info(f"  {key}: {data}")

        # Seed the database
        return self.seed_database()


if __name__ == "__main__":
    # Get database path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, "database_management_1.db")

    # Run seeding
    seeder = CollaborateurSeeder(db_path)
    records_inserted = seeder.run_seeding()

    print(f"\nSeeding completed! Inserted {records_inserted} collaborateur records.")
