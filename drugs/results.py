from django.http import HttpResponse
from django.template import loader
from drugs.models import Indication, Therapeutic
import pickle
from padelpy import from_smiles
import pandas as pd
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage
import dataframe_image as dfi
import tensorflow as tf
from tensorflow import keras
import rdkit
from rdkit import Chem

from IPython.display import Image

from rdkit.Chem import AllChem as Chem
from rdkit.Chem.Draw import IPythonConsole
from rdkit.Chem.Draw import SimilarityMaps
from rdkit.Chem import Draw

from rdkit.Chem.Fingerprints import FingerprintMols
from rdkit import DataStructs

from django.contrib.auth.decorators import login_required

import time

import matplotlib
matplotlib.use('Agg')

@login_required(login_url='login')
def index(request):
    if request.method == 'POST':
        print("Get request is called")

    if request.method == 'GET':
        print("Post request is called")

    template = loader.get_template('drugs/results.html')

    binary_prob = pd.read_csv("prob_binary.csv")
    mlc_prob = pd.read_csv("prob_mlc.csv")

    compounds = binary_prob["Compounds"].tolist()

    prob_data = {}
    targets = binary_prob.columns[1:len(binary_prob.columns)]
    similar_compounds = {}

    target_ids = {
        'EGFR': 'CHEMBL203',
        'IGF1R': 'CHEMBL1957',
        'MIA-PaCa': 'CHEMBL614725',
        'mTOR': 'CHEMBL2842'
    }

    train_data = pd.read_csv('Static/data/train-data.csv')

    k  = 0
    start = time.time()
    for c in compounds:
        prob_data[c] = {}
        img_name = 'C' + str(k)

        j = 0
        for i in range(0, len(targets)):
            prob_data[c][targets[i]] = {}
            prob_model1 = binary_prob[binary_prob["Compounds"] == c][targets[i]].tolist()[0]
            prob_model2 = mlc_prob[mlc_prob["Compounds"] == c][targets[i]].tolist()[0]
            prob_data[c][targets[i]]['probability'] = round(((prob_model1 + prob_model2) / 2) * 100, 2)


            if prob_data[c][targets[i]]['probability']  >= 50:
                print("inside if")
                tid = target_ids[targets[i]]
                smiles = train_data[train_data["target_chembl_ID"] == tid ]["canonical_smiles"].tolist()

                mol1 = Chem.MolFromSmiles(c)
                fp0 = FingerprintMols.FingerprintMol(mol1)
                compound_fig = Draw.MolToMPL(mol1, size=(120, 120))
                image_cf = img_name + '_qmol_.png'
                compound_fig.savefig('Static/pictures/similarity/' + image_cf, bbox_inches='tight')
                similar_compounds[c] = []
                for s in smiles:
                    if s != c:
                        mol2 = Chem.MolFromSmiles(s)
                        fp1 = FingerprintMols.FingerprintMol(mol2)

                        similarity = DataStructs.TanimotoSimilarity(fp0, fp1)
                        if similarity > 0.9:

                            fig, maxweight = SimilarityMaps.GetSimilarityMapForFingerprint(mol2,
                                                                                           mol1,
                                                                                           SimilarityMaps.GetMorganFingerprint,
                                                                                           metric=DataStructs.TanimotoSimilarity
                                                                                           )
                            name = img_name + '_' + str(j) + '.png'
                            fig.savefig('Static/pictures/similarity/' + name, bbox_inches='tight', pad_inches = 0,
                                        transparent = True, orientation="landscape")
                            r_compound_fig = Draw.MolToMPL(mol2, size=(120, 120))
                            image_rf = img_name + '_rmol_' + str(j) + '.png'
                            r_compound_fig.savefig('Static/pictures/similarity/' + image_rf, bbox_inches='tight')
                            new_sim = {'smile': s, 'similarity': round(similarity, 2), 'image': name, 'query': image_cf,
                                       'result': image_rf }
                            similar_compounds[c].append(new_sim)
                            j += 1
                    matplotlib.pyplot.clf()

        k += 1

    end = time.time()
    print('elapsed time ', end - start)
    context = { 'targets': targets, 'prob': prob_data, 'similar': similar_compounds }
    return HttpResponse(template.render(context, request))
# Create your views here.

