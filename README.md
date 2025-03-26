# Το web-app μπορεί να δοκιμαστεί από [εδώ](https://bio-thesis.streamlit.app/). 
# bioactivity-prediction-app
Χρησιμοποιώντας το πακέτο web service του ChEMBL, ανέκτησα δεδομένα βιοδραστικότητας που σχετίζονται με τη νόσο Αλτσχάιμερ και την κατάθλιψη. Από τα αποτελέσματα, επιλέχθηκαν εκείνα που αφορούν τον άνθρωπο (Homo sapiens). Το όνομα της πρωτεΐνης-στόχου είναι η "Αμυλοειδής-βήτα A4 πρωτεΐνη".

Στη συνέχεια, απομονώθηκαν οι τιμές IC50, οι οποίες μετρώνται σε νανομοριακές μονάδες (nM), και αποθηκεύτηκαν σε ένα αρχείο με όνομα Amyloid-beta-A4-protein.csv. Αφαιρέθηκαν τα δεδομένα που περιείχαν κενές τιμές (missing data). Συγκεκριμένα, αν κάποιο μόριο δεν είχε τιμή στη στήλη molecule_chembl_id, απορρίφθηκε, καθώς χωρίς αυτό δεν μπορούμε να τεκμηριώσουμε τις ιδιότητές του. Επίσης, αν δεν υπήρχε standard_value, δεν θα ήταν δυνατό να υπολογίσουμε τη βιοδραστικότητά του χωρίς να προβούμε σε υποθέσεις.

Στη συνέχεια, τα μόρια χαρακτηρίστηκαν ως ενεργά, ανενεργά ή ενδιάμεσα με βάση τις τιμές τους στην IC50. Συγκεκριμένα:

    Τιμές μικρότερες από 1.000 nM θεωρούνται ενεργές (active).

    Τιμές μεγαλύτερες από 10.000 nM θεωρούνται ανενεργές (inactive).

    Τιμές μεταξύ 1.000 και 10.000 nM θεωρούνται ενδιάμεσες (intermediate).

Για να μειώσω το μέγεθος του dataset, κράτησα μόνο τα απαραίτητα πεδία:

    action_type_action_type

    molecule_chembl_id

    canonical_smiles

    standard_value

Ένωσα τα επεξεργασμένα δεδομένα σε ένα νέο αρχείο bioactivity_preprocessed_data.csv, το οποίο περιέχει και την κατηγορία βιοδραστικότητας (bioactivity_class: inactive, active, intermediate).

Στη συνέχεια, πραγματοποιήθηκε υπολογισμός των descriptors και ανάλυση δεδομένων (Exploratory Data Analysis). Υπολογίστηκαν οι περιγραφείς του Lipinski, και έγινε μετατροπή των τιμών IC50 σε pIC50 χρησιμοποιώντας αρνητικό λογαριθμικό μετασχηματισμό. Παρουσιάστηκε η κατανομή των standard value μέσω διαγραμμάτων, έγινε κανονικοποίηση των δεδομένων και αφαιρέθηκε η κατηγορία intermediate για πιο καθαρή ανάλυση. Επίσης, δημιουργήθηκαν διαγράμματα συχνότητας για τις δύο κατηγορίες βιοδραστικότητας και box plots για την ανάλυση των κατανομών.

Στη συνέχεια, υπολογίστηκαν οι μοριακοί περιγραφείς (molecular descriptors), που αποτελούν ποσοτικές περιγραφές των χημικών δομών. Οι τιμές canonical_smiles αντιπροσωπεύουν τη χημική πληροφορία της δομής των ενώσεων. Χρησιμοποιήθηκε το εργαλείο PaDEL για τον υπολογισμό των descriptors και τελικά δημιουργήθηκε ένα dataset έτοιμο για την εκπαίδευση μοντέλων.

Για την εκπαίδευση των μοντέλων, αφαιρέθηκαν τα χαρακτηριστικά με χαμηλή διακύμανση (low variance features). Δοκιμάστηκαν διάφοροι αλγόριθμοι μηχανικής μάθησης για την κατασκευή μοντέλων παλινδρόμησης (regression). Οι πέντε κορυφαίοι αλγόριθμοι ήταν:

    LGBMRegressor

    GradientBoostingRegressor

    HistGradientBoostingRegressor

    SVR

    RandomForestRegressor

Οι επιδόσεις τους ήταν αρκετά κοντινές και ως αποτέλεσμα, δημιουργήθηκε το αρχείο descriptor_list.csv, το οποίο περιέχει τους μοριακούς περιγραφείς και τα χημικά αποτυπώματα (fingerprints) των ενώσεων.

Τέλος, ανέπτυξα μια εφαρμογή Streamlit σε μορφή web app, όπου ένας χρήστης μπορεί να ανεβάσει ένα αρχείο .txt με SMILES σημειογραφία που διαθέτει. Η εφαρμογή χρησιμοποιεί το εκπαιδευμένο μοντέλο μηχανικής μάθησης για να προβλέψει και να υπολογίσει τις βιοδραστικότητες των ενώσεων που περιλαμβάνονται στο αρχείο. Έτσι, η εφαρμογή μπορεί να χρησιμοποιηθεί για τον γρήγορο έλεγχο νέων μορίων και την αξιολόγηση της πιθανής δραστικότητάς τους.


# Reproducing this web app
To recreate this web app on your own computer, do the following:
```
cd E:\thesis-folder\Bioinformatics-project\bioactivity-prediction-app-main`
conda activate bio-project
conda install --file requirements.txt
```
### Create conda environment
```
conda create -n bioactivity python=3.7.9
```
Secondly, we will login to the *bioactivity* environement
```
conda activate bioactivity
```

### Generating the PKL file

The machine learning model used in this web app will firstly have to be generated by successfully running the included Jupyter notebook [bioactivity_prediction_app.ipynb](https://github.com/dataprofessor/bioactivity-prediction-app/blob/main/bioactivity_prediction_app.ipynb). Upon successfully running all code cells, a pickled model called acetylcholinesterase_model.pkl will be generated.

###  Launch the app

```
streamlit run app.py
```
