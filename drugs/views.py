from django.http import HttpResponse
from django.template import loader
from django.utils import asyncio

from drugs.models import Indications, Therapeutic_areas
import pickle
from padelpy import from_smiles
import pandas as pd
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage
import dataframe_image as dfi
from tensorflow import keras
import after_response
import os
import mimetypes
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import warnings
from django.template.loader import render_to_string, get_template
# from django_ztask.decorators import task


@login_required(login_url='/login')
def index(request):
    global flag
    flag = 0
    drug_dict = dict()
    theraput_list = Therapeutic_areas.objects.all().order_by('area_name').values_list('area_name', flat=True)
    for i in theraput_list:
        indicat_list = list(Indications.objects.filter(therapeutic_area__area_name=i).values_list('indication_name', flat=True))
        drug_dict[i] = indicat_list

    if request.method == 'POST':
        flag = 1
        global label, pred_prob
        global email
        email = None
        if request.user.is_authenticated:
            email = request.user.username
        indi = request.POST.get('indication')
        therepu = request.POST.get('therapeutic')
        csv_file = request.FILES['uploadedFile']
        some_var = request.POST.getlist('checks')
        # email = request.POST.get('emaill')
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'File is not csv type')
        else:
            file_data = pd.read_csv(csv_file, index_col=0)
        df = pd.DataFrame()

        ml_model.after_response(df, file_data, some_var, email)


        template = loader.get_template('drugs/ayus.html')
        # context = {'indication_list': indication_list,
        #            'model_list': therapeutic_list,
        #            'flagg': flag,
        #            'emailll': email}
        context = {'flagg': flag,
                   'emailll': email}
        return HttpResponse(template.render(context, request))

    else:
        template = loader.get_template('drugs/ayus.html')
        context = {'drug_dictionary': drug_dict,
                   'flagg': flag}
        return HttpResponse(template.render(context, request))
# Create your views here.


@after_response.enable
def ml_model(df, file_data, some_var, email):
    warnings.filterwarnings(action="ignore")
    print("In ASYNC Func....")
    for i in file_data.head(5)['canonical_smiles']:
        fingerprints = from_smiles(i, fingerprints=True, descriptors=False)
        if df.empty:
            df = pd.DataFrame.from_records([fingerprints])
        else:
            fd = pd.DataFrame.from_records([fingerprints])
            df = df.append(fd)
    df = df.reset_index()
    df = df.drop('index', axis=1)
    df = df.astype('str').astype('int')
    dictionary = dict()
    import os

    # path = "/Users/kausar/Documents/practicum-app/dti_web_app/"
    dict_mlc = dict()
    for i in some_var:
        if i == 'EGFR':
            # xpath = os.path.join(path, 'Static/Models/Binary/CHEMBL_203/rf.pkl')
            with open('Static/Models/Binary/CHEMBL_203/rf.pkl', 'rb') as file:
                # with open(xpath, 'rb') as file:
                pickle_model = pickle.load(file)
            prob = pickle_model.predict_proba(df)
            dictionary['EGFR'] = list(prob[:, 1]*100)
        elif i == 'IGF1R':
            # xpath = os.path.join(path, 'Static/Models/Binary/CHEMBL_1957/rf.pkl')
            with open('Static/Models/Binary/CHEMBL_1957/rf.pkl', 'rb') as file:
                # with open(xpath, 'rb') as file:
                print("in the section")
                pickle_model = pickle.load(file)
            prob = pickle_model.predict_proba(df)
            dictionary['IGF1R'] = list(prob[:, 1]*100)
        elif i == 'MIA-PaCa':
            # xpath = os.path.join(path, 'Static/Models/Binary/CHEMBL_614725/rf.pkl')
            with open('Static/Models/Binary/CHEMBL_614725/rf.pkl', 'rb') as file:
                # with open(xpath, 'rb') as file:
                pickle_model = pickle.load(file)
            prob = pickle_model.predict_proba(df)
            dictionary['MIA-PaCa'] = list(prob[:, 1]*100)
        else:
            # xpath = os.path.join(path, 'Static/Models/Binary/CHEMBL_2842/rf.pkl')
            # with open(xpath, 'rb') as file:
            with open('Static/Models/Binary/CHEMBL_2842/rf.pkl', 'rb') as file:
                pickle_model = pickle.load(file)
            prob = pickle_model.predict_proba(df)
            dictionary['mTOR'] = list(prob[:, 1]*100)
    gd = pd.DataFrame(dictionary, index=file_data.head(5)['canonical_smiles'].values)
    # gd = gd.rename_axis(index='Compounds', columns='Targets')
    # xpath = os.path.join(path, 'Static/Models/MLC/mlc_model.h5')
    mlc_model = keras.models.load_model('Static/Models/MLC/mlc_model.h5')
    prob = mlc_model.predict_proba(df)

    for j in some_var:
        if j == 'EGFR':
            dict_mlc['EGFR'] = list(prob[:, 3]*100)
        elif j == 'IGF1R':
            dict_mlc['IGF1R'] = list(prob[:, 1]*100)
        elif j == 'MIA-PaCa':
            dict_mlc['MIA-PaCa'] = list(prob[:, 0]*100)
        elif j == 'mTOR':
            dict_mlc['mTOR'] = list(prob[:, 2]*100)

    gd_mlc = pd.DataFrame(dict_mlc, index=file_data.head(5)['canonical_smiles'].values)

    df_avg = pd.DataFrame(columns=['EGFR', 'IGF1R', 'MIA-PaCa', 'mTOR'])
    df_avg['EGFR'] = (gd['EGFR'] + gd_mlc['EGFR']) / 2
    df_avg['IGF1R'] = (gd['IGF1R'] + gd_mlc['IGF1R']) / 2
    df_avg['MIA-PaCa'] = (gd['MIA-PaCa'] + gd_mlc['MIA-PaCa']) / 2
    df_avg['mTOR'] = (gd['mTOR'] + gd_mlc['mTOR']) / 2
    df_avg = df_avg.rename_axis(index='Compounds', columns='Targets')
    df_styled = df_avg.style.applymap(color_)
    df_styled = df_styled.format({
            'EGFR': '{:,.2f}%'.format,
            'IGF1R': '{:,.2f}%'.format,
            'MIA-PaCa': '{:,.2f}%'.format,
            'mTOR': '{:,.2f}%'.format,
        })
    df_styled = df_styled.set_caption("\nResults")
    dfi.export(df_styled, 'table1.png')
    subject = 'Welcome to "Drogue Cibler"'
    message = 'Hi, user \nThank you for registering in DTI.'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email, ]
    mail = EmailMessage(subject, message, email_from, recipient_list)
    mail.attach_file('table1.png')
    mail.send()
    print("------------------COMPLETED!--------------------")


def download_file(request):
    # fill these variables with real values
    current_path = os.path.dirname(__file__)
    filename = 'example_input.csv'
    #fl = os.path.join(current_path, filename)
    #fl_path = 'drugs/'

    #fl = open(current_path, 'r')
    fl = open(os.path.join(current_path, filename))
    mime_type, _ = mimetypes.guess_type(current_path)
    response = HttpResponse(fl, content_type=mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response


def color_(val):
    if val >= 0.0 and val < 30:
        color = 'red'
    elif val >= 0.3 and val < 80:
        color = 'darkorange'
    else:
        color = 'green'
    return 'color: %s' % color