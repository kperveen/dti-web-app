from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import Target, Indication, Model, Compound, Therapeutic
import pickle
from padelpy import from_smiles
import pandas as pd
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail, EmailMessage
import dataframe_image as dfi
import mimetypes
import os

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

def index(request):
    indication_list = []
    therapeutic_list = []
    global flag
    flag = 0
    il = Indication.objects.order_by()
    ml = Therapeutic.objects.order_by()
    for j in il:
        indication_list.append(j.indication_text)
    for k in ml:
        therapeutic_list.append(k.therapeutic_text)

    if request.method == 'POST':
        flag = 1
        global label, pred_prob
        indi = request.POST.get('indication')
        therepu = request.POST.get('therapeutic')
        csv_file = request.FILES['uploadedFile']
        some_var = request.POST.getlist('checks')
        email = request.POST.get('emaill')
        # print(email)
        # print(some_var)
        # print(email)
        # print(some_var)
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'File is not csv type')
        else:
            file_data = pd.read_csv(csv_file, index_col=0)
        indi_ind = indication_list.index(indi)
        modl_ind = therapeutic_list.index(therepu)
        indication_list[0], indication_list[indi_ind] = indication_list[indi_ind], indication_list[0]
        therapeutic_list[0], therapeutic_list[modl_ind] = therapeutic_list[modl_ind], therapeutic_list[0]
        df = pd.DataFrame()
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
        for i in some_var:
            if i == 'EGFR':
                with open('Static/Models/Binary/CHEMBL_203/rf.pkl', 'rb') as file:
                    print("in the section")
                    pickle_model = pickle.load(file)
                prob = pickle_model.predict_proba(df)
                dictionary['EGFR'] = list(prob[:, 1])
                # print(prob[:, 1])
                # print(pickle_model.predict(df))
            elif i == 'IGF1R':
                with open('Static/Models/Binary/CHEMBL_1957/rf.pkl', 'rb') as file:
                    print("in the section")
                    pickle_model = pickle.load(file)
                prob = pickle_model.predict_proba(df)
                dictionary['IGF1R'] = list(prob[:, 1])
            elif i == 'MIA-PaCa-2':
                with open('Static/Models/Binary/CHEMBL_614725/rf.pkl', 'rb') as file:
                    print("in the section")
                    pickle_model = pickle.load(file)
                prob = pickle_model.predict_proba(df)
                dictionary['MIA-PaCa-2'] = list(prob[:, 1])
            else:
                with open('Static/Models/Binary/CHEMBL_2842/rf.pkl', 'rb') as file:
                    print("in the section")
                    pickle_model = pickle.load(file)
                prob = pickle_model.predict_proba(df)
                dictionary['mTOR'] = list(prob[:, 1])
        gd = pd.DataFrame(dictionary, index=file_data.head(5)['canonical_smiles'].values)
        gd = gd.rename_axis(index='Compounds', columns='Targets')

        # print(gd)
        df_styled = gd.style.applymap(color_)
        df_styled = df_styled.set_caption("\nResults with Binary Classification")
        dfi.export(df_styled, 'table.png')
        subject = 'welcome to GFG world'
        message = 'Hi thank you for registering in geeksforgeeks.'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email, ]
        mail = EmailMessage(subject, message, email_from, recipient_list)
        mail.attach_file('table.png')
        mail.send()

    # template = loader.get_template('drugs/ayus.html')
    # context = {'targets_list': target_list,
    #            'indication_list': indication_list,
    #            'model_list': therapeutic_list,
    #            'compound_list': canonical_smiles,
    #            'label_list': label,
    #            'pred_probab': pred_prob*100,
    #            'flagg': flag}
    template = loader.get_template('drugs/ayus.html')
    context = {'indication_list': indication_list,
               'model_list': therapeutic_list,
               'flagg': flag}
    # print(context)
    return HttpResponse(template.render(context, request))
# Create your views here.


def color_(val):
    if val >= 0.0 and val < 0.3:
        color = 'red'
    elif val >= 0.3 and val < 0.8:
        color = 'darkorange'
    else:
        color = 'green'
    return 'color: %s' % color