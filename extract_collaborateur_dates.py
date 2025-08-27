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

class CollaborateurDateExtractor:
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
            nom = ' '.join(parts[:-1])
            return nom, prenom
        return name, None
    
    def parse_date(self, date_str) -> Optional[date]:
        """Parse various date formats to standard date object"""
        if not date_str or pd.isna(date_str) or str(date_str).strip() == '' or str(date_str).upper() in ['A PASSER', 'DISPENSÉ', 'ABSENT', 'EN COURS']:
            return None
            
        date_str = str(date_str).strip()
        
        # Try different date formats
        formats = [
            '%d/%m/%Y',
            '%d/%m/%y', 
            '%m/%d/%y',
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%d-%m-%Y'
        ]
        
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                # If year is less than 50, assume it's 20xx, otherwise 19xx
                if fmt in ['%d/%m/%y', '%m/%d/%y'] and parsed_date.year < 1950:
                    parsed_date = parsed_date.replace(year=parsed_date.year + 100)
                return parsed_date.date()
            except ValueError:
                continue
                
        logger.warning(f"Could not parse date: {date_str}")
        return None
    
    def extract_visite_medicale(self):
        """Extract medical visit dates from APST file"""
        logger.info("Extracting Visite Médicale dates...")
        try:
            with open('APST - FICHIER DU PERSONNEL...csv', 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines[3:]:  # Skip first 3 lines
                line = line.strip()
                if not line or len(line) < 10:  # Skip empty or very short lines
                    continue
                
                # Look for date pattern first
                date_pattern = r'\d{1,2}/\d{1,2}/\d{4}'
                date_matches = re.findall(date_pattern, line)
                
                # Split by whitespace but be more careful with names
                parts = line.split()
                if len(parts) >= 2 and not line.upper().startswith('NOMS'):
                    # Handle compound names better
                    if len(parts) >= 3 and parts[2] not in date_matches:
                        # Check if this might be a compound last name
                        nom = f"{parts[0]} {parts[1]}"
                        prenom = parts[2]
                    else:
                        nom = parts[0]
                        prenom = parts[1]
                    
                    # Skip header-like entries
                    if nom.upper() in ['LISTE', 'NOMS', 'PRÉNOMS', 'DATE', 'MEDICA', 'BOURGEO']:
                        continue
                    
                    visite_med = None
                    if date_matches:
                        visite_med = self.parse_date(date_matches[0])
                    
                    # Normalize names
                    nom = nom.upper().strip()
                    prenom = prenom.upper().strip()
                    
                    if nom and prenom and len(nom) > 1 and len(prenom) > 1:
                        key = f"{nom}_{prenom}"
                        
                        self.collaborateurs_data[key] = {
                            'nom': nom,
                            'prenom': prenom,
                            'ifo': None,
                            'caces': None,
                            'airr': None,
                            'hgo': None,
                            'bo': None,
                            'visite_med': visite_med,
                            'brevet_secour': None
                        }
            
            logger.info(f"Extracted medical visit dates for {len(self.collaborateurs_data)} employees")
            
        except Exception as e:
            logger.error(f"Error extracting medical visit dates: {e}")
    
    def extract_brevet_secourisme(self):
        """Extract first aid certification dates"""
        logger.info("Extracting Brevet Secourisme dates...")
        try:
            df = pd.read_csv('SECOURISTE EN COURS.csv', sep=';', skiprows=10)
            
            for _, row in df.iterrows():
                if pd.notna(row.iloc[0]) and str(row.iloc[0]).strip():
                    name = str(row.iloc[0]).strip()
                    nom, prenom = self.normalize_name(name)
                    
                    if nom:
                        key = f"{nom}_{prenom}" if prenom else nom
                        
                        # Get certification date from column 2
                        brevet_secour = None
                        if len(row) > 2 and pd.notna(row.iloc[2]):
                            brevet_secour = self.parse_date(row.iloc[2])
                        
                        # Update existing record or create new one
                        if key in self.collaborateurs_data:
                            self.collaborateurs_data[key]['brevet_secour'] = brevet_secour
                        else:
                            self.collaborateurs_data[key] = {
                                'nom': nom,
                                'prenom': prenom,
                                'ifo': None,
                                'caces': None,
                                'airr': None,
                                'hgo': None,
                                'bo': None,
                                'visite_med': None,
                                'brevet_secour': brevet_secour
                            }
            
            logger.info("Extracted first aid certification dates")
            
        except Exception as e:
            logger.error(f"Error extracting first aid dates: {e}")
    
    def extract_ifo_caces_data(self):
        """Extract IFO (FIMO) and CACES dates from CACES file"""
        logger.info("Extracting IFO and CACES dates...")
        try:
            with open('AAAAAAAAAAAAA -Tableau information et formation CACES - FIMO.csv', 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            for line in lines:
                # Look for lines that start with employee names
                if re.match(r'^[A-Z][A-Z\s]+ [A-Z]', line.strip()):
                    parts = line.split()
                    if len(parts) >= 2:
                        potential_nom = parts[0]
                        potential_prenom = parts[1]
                        
                        nom, prenom = self.normalize_name(f"{potential_nom} {potential_prenom}")
                        
                        if nom:
                            key = f"{nom}_{prenom}" if prenom else nom
                            
                            # Extract all dates from the line
                            date_pattern = r'(\d{1,2}/\d{1,2}/\d{4})'
                            dates = re.findall(date_pattern, line)
                            
                            # Try to identify IFO and CACES dates
                            # IFO (FIMO) is typically around index 4-6 in the dates
                            # CACES dates are typically later in the line
                            ifo_date = None
                            caces_date = None
                            
                            if len(dates) >= 4:
                                # Skip birth date (first date) and look for FIMO
                                for i in range(1, min(6, len(dates))):
                                    potential_ifo = self.parse_date(dates[i])
                                    if potential_ifo and potential_ifo.year >= 2000:  # FIMO dates should be recent
                                        ifo_date = potential_ifo
                                        break
                                
                                # Look for CACES dates (usually later in the sequence)
                                for i in range(6, len(dates)):
                                    potential_caces = self.parse_date(dates[i])
                                    if potential_caces and potential_caces.year >= 2000:
                                        caces_date = potential_caces
                                        break
                            
                            # Update existing record or create new one
                            if key in self.collaborateurs_data:
                                if ifo_date:
                                    self.collaborateurs_data[key]['ifo'] = ifo_date
                                if caces_date:
                                    self.collaborateurs_data[key]['caces'] = caces_date
                            else:
                                self.collaborateurs_data[key] = {
                                    'nom': nom,
                                    'prenom': prenom,
                                    'ifo': ifo_date,
                                    'caces': caces_date,
                                    'airr': None,
                                    'hgo': None,
                                    'bo': None,
                                    'visite_med': None,
                                    'brevet_secour': None
                                }
            
            logger.info("Extracted IFO and CACES dates")
            
        except Exception as e:
            logger.error(f"Error extracting IFO/CACES dates: {e}")
    
    def extract_hgo_bo_airr_data(self):
        """Extract HGO, BO, and AIRR dates from Planning Formations file"""
        logger.info("Extracting HGO, BO, and AIRR dates...")
        try:
            with open('PLANNING FORMATIONS.csv', 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Find the data section (after headers)
            data_started = False
            for line in lines:
                line = line.strip()
                if not line or len(line) < 10:
                    continue
                
                # Skip header lines
                if any(header in line.upper() for header in ['FORMATION VALIDE', 'FORMATION A ECHEANCE', 'FORMATION A PROGRAMMER', 'ARRET LONGUE MALADIE', 'FORMATIONS', 'BH-HF/BO-HO', 'AIPR', 'SECOURISTES', 'DATES DE FORMATION', 'DATES DE VALIDITE']):
                    continue
                
                # Look for employee data lines
                parts = line.split()
                if len(parts) >= 2:
                    # First two parts should be name
                    nom = parts[0].upper()
                    prenom = parts[1].upper()
                    
                    # Skip obvious non-names
                    if nom in ['NOMS', 'PRENOMS', 'DATES'] or len(nom) < 2 or len(prenom) < 2:
                        continue
                    
                    key = f"{nom}_{prenom}"
                    
                    # Extract dates from the line
                    date_pattern = r'\d{1,2}/\d{1,2}/\d{4}'
                    dates = re.findall(date_pattern, line)
                    
                    # Try to map dates to correct fields
                    hgo_date = None
                    bo_date = None  
                    airr_date = None
                    
                    # Parse dates based on position and context
                    if len(dates) >= 2:
                        # First date pair usually for BO/HGO
                        hgo_date = self.parse_date(dates[0])  # Formation date
                        bo_date = self.parse_date(dates[1])   # Validity date
                        
                    if len(dates) >= 4:
                        # Second pair for AIRR
                        airr_date = self.parse_date(dates[2])  # AIRR formation date
                    
                    # Update existing record or create new one
                    if key in self.collaborateurs_data:
                        if hgo_date:
                            self.collaborateurs_data[key]['hgo'] = hgo_date
                        if bo_date:
                            self.collaborateurs_data[key]['bo'] = bo_date
                        if airr_date:
                            self.collaborateurs_data[key]['airr'] = airr_date
                    else:
                        # Only create if we have valid name and at least one date
                        if (hgo_date or bo_date or airr_date) and nom and prenom:
                            self.collaborateurs_data[key] = {
                                'nom': nom,
                                'prenom': prenom,
                                'ifo': None,
                                'caces': None,
                                'airr': airr_date,
                                'hgo': hgo_date,
                                'bo': bo_date,
                                'visite_med': None,
                                'brevet_secour': None
                            }
            
            logger.info("Extracted HGO, BO, and AIRR dates")
            
        except Exception as e:
            logger.error(f"Error extracting HGO/BO/AIRR dates: {e}")
    
    def seed_database(self):
        """Seed the database with extracted date data"""
        logger.info("Seeding database with date data...")
        
        try:
            # Connect to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Clear existing data
            cursor.execute('DELETE FROM collaborateurs')
            logger.info("Cleared existing collaborateurs data")
            
            # Insert consolidated data
            inserted_count = 0
            for key, data in self.collaborateurs_data.items():
                try:
                    cursor.execute('''
                        INSERT INTO collaborateurs (
                            nom, prenom, ifo, caces, airr, hgo, bo, 
                            visite_med, brevet_secour, commentaire
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        data['nom'],
                        data['prenom'],
                        data['ifo'],
                        data['caces'],
                        data['airr'], 
                        data['hgo'],
                        data['bo'],
                        data['visite_med'],
                        data['brevet_secour'],
                        None  # No commentaire as requested
                    ))
                    inserted_count += 1
                except Exception as e:
                    logger.warning(f"Error inserting record for {key}: {e}")
            
            conn.commit()
            conn.close()
            
            logger.info(f"Successfully seeded database with {inserted_count} collaborateur records")
            return inserted_count
            
        except Exception as e:
            logger.error(f"Error seeding database: {e}")
            raise
    
    def print_extracted_data(self):
        """Print extracted data in tab-separated format"""
        print("\nExtracted Data:")
        print("Nom\tPrénom\tIFO\tCACES\tAIRR\tHGO\tBO\tVisite Médicale\tBrevet Secourisme")
        print("-" * 100)
        
        for key, data in self.collaborateurs_data.items():
            print(f"{data['nom']}\t{data['prenom']}\t{data['ifo'] or ''}\t{data['caces'] or ''}\t{data['airr'] or ''}\t{data['hgo'] or ''}\t{data['bo'] or ''}\t{data['visite_med'] or ''}\t{data['brevet_secour'] or ''}")
    
    def run_extraction(self):
        """Run the complete extraction process"""
        logger.info("Starting collaborateur date extraction process...")
        
        # Extract data from all CSV sources
        self.extract_visite_medicale()
        self.extract_brevet_secourisme() 
        self.extract_ifo_caces_data()
        self.extract_hgo_bo_airr_data()
        
        logger.info(f"Total unique collaborateurs consolidated: {len(self.collaborateurs_data)}")
        
        # Print extracted data
        self.print_extracted_data()
        
        # Seed the database
        return self.seed_database()

if __name__ == "__main__":
    # Get database path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, 'database_management_1.db')
    
    # Run extraction
    extractor = CollaborateurDateExtractor(db_path)
    records_inserted = extractor.run_extraction()
    
    print(f"\nExtraction completed! Inserted {records_inserted} collaborateur records with date data.")
