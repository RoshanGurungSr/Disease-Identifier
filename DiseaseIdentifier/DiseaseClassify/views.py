from django.shortcuts import render
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.decorators import login_required
from DiseaseClassify.forms import UserSignupForm
from django.shortcuts import redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import logging
from django.http import HttpResponse

# Database
from .models import UploadImage
from DiseaseClassify.forms import PredictImage,UpdatePred,AddPred

import h5py
from flask import send_from_directory
import os
from uuid import uuid4

# Convolutional Neural Network
from scipy.misc import imsave, imread, imresize
import numpy as np
import keras.models
import re
import sys
import os

# sys.path.append(os.path.abspath("./model"))
# from load import *
import tensorflow as tf
from keras.models import load_model
from keras.preprocessing.image import ImageDataGenerator,image

APP_ROOT=os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def index(request):
	# if request.user.is_authenticated():
	# 	return redirect('home')
	# else:
	# 	return render(request, 'index.html',)

	return render(request, 'index.html',)

def contact(request):
	return render(request, 'contact.html',)

@login_required
def home(request):
	
	from keras import backend as K
	K.clear_session()
	
	showAll= UploadImage.objects.filter(name=request.user)

	form = PredictImage()
	if request.method == "POST":
		
		form = PredictImage(request.POST, request.FILES)
		if form.is_valid():
			predict = form.save(commit=False)
			predict.name = request.user
			predict.save()
			return redirect('upload')

		else:
			form = PredictImage()

	context_dict = {
		'form' : form,
		'showAll':showAll,}
	return render(request,"home.html",context_dict)


def user_registration(request):
	if request.method == 'POST':
		form=UserSignupForm(request.POST)
		if form.is_valid():
			form.save()
		
		messages.success(request,"Account Created Successfully")
		print(request.FILES.getlist("file"))
		return redirect('home')
		
	else:
		form = UserSignupForm()
	
	return render(request,'registration/signup.html',{'form':form})



@login_required
def upload(request):
	latest = UploadImage.objects.last()
	# print("Latest Image",latest.predict_image.url)
	# filename=latest.predict_image.url

	# File path
	filename = os.path.join(BASE_DIR+"/"+latest.predict_image.url)
	file_path = os.path.join(BASE_DIR, 'models/modelMultipleClass2.h5')


	#  CNN prediction
	model = load_model(file_path)
	img = image.load_img(filename,target_size=(150,150))
	img = image.img_to_array(img)
	img = np.expand_dims(img,axis=0)
	result = model.predict(img)
	predicted_class_indices=np.argmax(result,axis=1)

	probabilities = model.predict_proba(img)

	if predicted_class_indices[0]==0:
		lass_name="Apple"
		prediction = "Frogeye_Spot"
	elif predicted_class_indices[0]==1:
		class_name="Apple"
		prediction="Healthy"
	elif predicted_class_indices[0]==2:
		class_name="Tomato"
		prediction="Leaf_Mold"
	elif predicted_class_indices[0]==3:
		class_name="Tomato"
		prediction="Healthy"
	

	form = AddPred(request.POST, request.FILES, instance=latest)
	
	if form.is_valid():
		updatePred = form.save(commit=False)
		updatePred.prediction = prediction
		updatePred.save()

	form = AddPred(instance=latest)
	# # form.save()

	context_dict = {
		'imagePath':latest,
		'class':class_name,
		'prediction':prediction,
		'form':form,
	}
	return render(request,'result.html',context_dict)


def resubmit(request):
    from keras import backend as K
    K.clear_session()

    return redirect('home')


def report(request):
	showAll= UploadImage.objects.filter(name=request.user)
	print(showAll)

	context_dict = {
		'showAll':showAll,
	}

	return render(request,"report.html",context_dict)




# def upload(request):
#     target = os.path.join(APP_ROOT, 'images/')
#     print(target)
#     if not os.path.isdir(target):
#         os.mkdir(target)
#     else:
#         print("Couldn't create upload directory or already created: {}".format(target))
#     print(request.FILES.getlist("file"))
#     for upload in request.FILES.getlist("file"):
#         print("This is upload",upload)
#         print("{} is the file name".format(upload.name))
#         # global filename
#         filename = upload.name
#         destination = "/".join([target, filename])
#         # print ("Accept incoming file:", filename)
#         # print ("Save it to:", destination)
#         upload.save(destination)

#         # CNN prediction
#         model = load_model('model/modelMultipleClass2.h5')
#         img = image.load_img('images/{}'.format(filename),target_size=(150,150))
#         img = image.img_to_array(img)
#         img = np.expand_dims(img,axis=0)
#         result = model.predict(img)
#         predicted_class_indices=np.argmax(result,axis=1)

#         if predicted_class_indices[0]==0:
#             class_name="Apple"
#             prediction = "Frogeye_Spot"
#         elif predicted_class_indices[0]==1:
#             class_name="Apple"
#             prediction="Healthy"
#         elif predicted_class_indices[0]==2:
#             class_name="Tomato"
#             prediction="Leaf_Mold"
#         elif predicted_class_indices[0]==3:
#             class_name="Tomato"
#             prediction="Healthy"


#     return send_from_directory("images", filename, as_attachment=True)
#     return render(request,"result.html", image_name=filename, result=prediction,class_name=class_name,)

# def submit_image(filename):
#     return send_from_directory("images", filename)







# Backups
# def test(request):
# 	form = PredictImage()
# 	if request.method == "POST":
		
# 		form = PredictImage(request.POST, request.FILES)
# 		if form.is_valid():
# 			predict = form.save(commit=False)
# 			predict.name = request.user
# 			predict.save()
# 			return redirect('home')

# 		else:
# 			form = PredictImage()

# 	context_dict = {'form' : form}
# 	return render(request,"test.html",context_dict)