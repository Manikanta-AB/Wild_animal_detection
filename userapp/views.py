

from django.shortcuts import render , redirect
from userapp.models import *
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
import urllib.request
import urllib.parse
import random
import string
from django.utils.datastructures import MultiValueDictKeyError
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from tensorflow.keras.applications.inception_v3 import preprocess_input
#import tensorflow.keras.applications.inception_v3 as inception_v3

from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from PIL import Image
import numpy as np
from django.core.files.storage import default_storage
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.inception_v3 import preprocess_input
from tensorflow.keras.models import load_model
import numpy as np

from twilio.rest import Client
import cv2
import matplotlib.pyplot as plt

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
import urllib.request
import urllib.parse


# model = load_model('model_inception')
# model=load_model(r"C:\Lumpy Disease Full Stack\Lumphy_model.h5")


# Create your views here.

def user_index(request):
    return render(request,'user/index.html')

def user_about(request):
    return render(request,'user/about.html')

def user_contact(request):
    return render(request,'user/contact.html')


def user_services(request):
    return render(request,'user/service.html')

def user_wilddetect(request):
      return render(request,'user/wilddetect.html')

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(email,password,'jjjjjjjjjjjjjjjjjj')
        try : 
            user_data = UserModels.objects.get(email = email)
            print(user_data)
             
            if user_data.password ==  password:
                if user_data.user_status == 'accepted':
                    if user_data.Otp_Status == 'verified':
                       messages.success(request,'login successfull')
                       request.session['user_id'] = user_data.user_id
                       request.session['emil'] = email
                       print('login sucessfull')
                       return redirect('user_dashboard')
                    else:
                        return redirect('otp')
                elif user_data.password == password and user_data.user_status == 'rejected':
                    messages.warning(request,"your account is rejected")
                else:
                    messages.info(request,"your account is in pending")
            else:
                messages.error(request, 'Error in Email or Password')
        except:
            print('exce[t]')
            return redirect('user_login')
    return render(request,'user/userlogin.html')

def admin_login(request):
    admin_name = 'admin@gmail.com'
    admin_pwd = 'admin'
    if request.method == 'POST':
        a_name = request.POST.get('email')
        a_pwd = request.POST.get('password')
        print(a_name, a_pwd, 'admin entered details')

        if admin_name == a_name and admin_pwd == a_pwd:
            messages.success(request, 'login successful')
            return redirect('admin_index')
        else:
            messages.error(request, 'Wrong Email Or Password')
            return redirect('admin_login')   
    return render(request,'user/adminlogin.html')

def sendSMS(user, otp, mobile):
    data = urllib.parse.urlencode({
        'username': 'Codebook',
        'apikey': '56dbbdc9cea86b276f6c',
        'mobile': mobile,
        'message': f'Hello {user}, your OTP for account activation is {otp}. This message is generated from https://www.codebook.in server. Thank you',
        'senderid': 'CODEBK'
    })
    data = data.encode('utf-8')
    # Disable SSL certificate verification
    # context = ssl._create_unverified_context()
    request = urllib.request.Request("https://smslogin.co/v3/api.php?")
    f = urllib.request.urlopen(request, data)
    return f.read()


def user_registration(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        username = request.POST.get('user')
        email = request.POST.get('email')
        contact = request.POST.get ('contact')
        password = request.POST.get('password')
        file = request.FILES['file']
        # file = request.FILES['file']
        print (request)
        print(name,username,email,contact,password,'data')
        otp = str(random.randint(1000, 9999)) 
        print(otp)
        try:
           print('try')
           UserModels.objects.get(email=email,) 
           messages.info(request, 'Mail already Registered')
           return redirect('user_registration') 
        except:
            print('except')
            # mail message
            mail_message = f'Registration Successfully\n Your 4 digit Pin is below\n {otp}'
            print(mail_message)
            send_mail("Student Password", mail_message, settings.EMAIL_HOST_USER,[email])
            # text nessage
            sendSMS(name, otp, contact)
            UserModels.objects.create( otp=otp,email=email ,password=password,name=name,contact=contact, file=file )        
            request.session['email'] = email
            messages.success(request, 'Register Successfull...!')
            return redirect('user_otp')
    return render(request,'user/register.html')


def user_otp (request):
    user_id = request.session['email']
    user_o =UserModels.objects.get(email = user_id)
    print(user_o,'user available')
    print(type(user_o.otp))
    print(user_o. otp,'created otp')
    # print(user_o. otp, 'creaetd otp')
    if request.method == 'POST':
        u_otp = request.POST.get('otp')
        u_otp = int(u_otp)
        print(u_otp, 'enter otp')
        if u_otp == user_o.otp:
            print('if')
            user_o.Otp_Status  = 'verified'
            user_o.save()
            messages.success(request, 'OTP  verified successfully')
            return redirect('user_login')
        else:
            print('else')
            messages.error(request, 'Error in OTP')
            return redirect('user_otp')
    return render(request,'user/otp.html')

def user_dashboard(request):
    return render(request,'user/dashboard.html')
def user_myprofile(request):
    user_id = request.session['user_id']
    example = UserModels.objects.get(user_id = user_id)
    print(example,'user_id')
    if request.method == 'POST' :
        name = request.POST.get('name')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        password = request.POST.get('password')
        messages.success(request,'updated successful')

        example.name =name
        example.contact =contact
        example.email =email
        example.password =password
        
        if len(request.FILES)!=0:
            file = request.FILES['file']
            example.file = file
            example.name = name
            example.contact = contact
            example.email = email
            example.password = password
            example.save()
        else:
            example.name = name
            example.email = email
            example.password = password
            example.contact = contact
        #    example.file=file
            example.save()     
    return render(request,'user/myprofile.html',{'i':example})



def user_feedback(request):
    views_id = request.session['user_id']
    user = UserModels.objects.get(user_id = views_id)
    if request.method == 'POST':
        u_feedback = request.POST.get('feedback')
        u_rating = request.POST.get('rating')
        if not user_feedback:
            return redirect('')
        sid=SentimentIntensityAnalyzer()
        score=sid.polarity_scores(u_feedback)
        sentiment=None
        if score['compound']>0 and score['compound']<=0.5:
            sentiment='positive'
        elif score['compound']>=0.5:
            sentiment='very positive'
        elif score['compound']<-0.5:
            sentiment='very negative'
        elif score['compound']<0 and score['compound']>=-0.5:
            sentiment='negative'
        else :
            sentiment='neutral'
        print(sentiment)
        user.star_feedback=u_feedback
        user.star_rating = u_rating
        user.save()
        UserFeedbackModels.objects.create(user_details = user, star_feedback = u_feedback, star_rating = u_rating, sentment= sentiment)
        messages.success(request,'Thankyou For Your Feedback')
    rev=UserFeedbackModels.objects.filter()    
    return render(request,'user/feedback.html')



model = load_model(r"wild_model.h5")
class_labels = [
    'Human Being Detected',
    'Domestic Animal Detected',
    'Wild Animal Detected'
]


def user_quality(request):
    result = "No image uploaded"
    uploaded_image_url = None  # Initialize the image URL
    user_id = request.session['email']
    print(user_id)

    if request.method == "POST" and 'image' in request.FILES:
        uploaded_image = request.FILES['image']
        file_path = default_storage.save(uploaded_image.name, uploaded_image)
        path = settings.MEDIA_ROOT + '/' + file_path
        uploaded_image_url = default_storage.url(file_path)  # Get the URL of the uploaded image
        print(path)

        # Load an image from file
        image_frame = cv2.imread(path)
        result = prediction(path)
        print(result)

        if result == "Wild Animal Detected":
            # Create subplots to display original, color, and grayscale images
            fig, axes = plt.subplots(1, 3, figsize=(15, 5))

            # Display the original image
            axes[0].imshow(cv2.cvtColor(image_frame, cv2.COLOR_BGR2RGB))
            axes[0].axis('off')
            axes[0].set_title("Original Image")
            a = "✅\nAccuracy: 99.04%"
            b = "❌\nAccuracy: 99.04%"

            # Make predictions in color and display in subplot
            predict_and_display(image_frame, model, class_labels, display_mode='color', ax=axes[1])

            # Make predictions in grayscale and display in subplot
            predict_and_display(image_frame, model, class_labels, display_mode='grayscale', ax=axes[2])

            plt.show()

            result = prediction(path)
            print(result)
            messages.success(request, 'Wild Animal result Detected Successfully..✅Accuracy: 99.04%')
            send_email_alert(path,user_id)

        if result == "Human Being Detected":
            # Create subplots to display original, color, and grayscale images
            fig, axes = plt.subplots(1, 3, figsize=(15, 5))

            # Display the original image
            axes[0].imshow(cv2.cvtColor(image_frame, cv2.COLOR_BGR2RGB))
            axes[0].axis('off')
            axes[0].set_title("Original Image")


            # Make predictions in color and display in subplot
            predict_and_display(image_frame, model, class_labels, display_mode='color', ax=axes[1])

            # Make predictions in grayscale and display in subplot
            predict_and_display(image_frame, model, class_labels, display_mode='grayscale', ax=axes[2])

            plt.show()

            result = prediction(path)
            print(result)
            messages.success(request, 'Human Being Detected ..✅Accuracy: 99.04%')

        if result == "Domestic Animal Detected":
            # Create subplots to display original, color, and grayscale images
            fig, axes = plt.subplots(1, 3, figsize=(15, 5))

            # Display the original image
            axes[0].imshow(cv2.cvtColor(image_frame, cv2.COLOR_BGR2RGB))
            axes[0].axis('off')
            axes[0].set_title("Original Image")


            # Make predictions in color and display in subplot
            predict_and_display(image_frame, model, class_labels, display_mode='color', ax=axes[1])

            # Make predictions in grayscale and display in subplot
            predict_and_display(image_frame, model, class_labels, display_mode='grayscale', ax=axes[2])

            plt.show()

            result = prediction(path)
            print(result)
            messages.success(request, 'Domestic Animal Detected Successfully..✅Accuracy: 99.04%')




    return render(request, 'user/wilddetect.html', {'result': result, 'uploaded_image_url': uploaded_image_url})


def predict_and_display(frame, model, class_labels, display_mode='color', ax=None):

    img = cv2.resize(frame, (224, 224))
    img_array = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)

    prediction = model.predict(img_array)
    predicted_class_index = np.argmax(prediction)
    predicted_class_label = class_labels[predicted_class_index]

    if display_mode == 'color':
        display_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        title = f"Predicted Class: {predicted_class_label}"
    elif display_mode == 'grayscale':
        display_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        title = f"Gray Scale: {predicted_class_label}"
    else:
        raise ValueError("Invalid display_mode. Use 'color' or 'grayscale'.")

    if ax is not None:
        ax.imshow(display_img, cmap='gray' if display_mode == 'grayscale' else None)
        ax.axis('off')
        ax.set_title(title)
    else:
        plt.imshow(display_img, cmap='gray' if display_mode == 'grayscale' else None)
        plt.axis('off')
        plt.title(title)
        plt.show()

# Example usage:
# predict_and_display(frame, model, class_labels, display_mode='grayscale')  # Adjust parameters as needed



def prediction(path):
    img = image.load_img(path, target_size=(224, 224))
    i = image.img_to_array(img)
    i = np.expand_dims(i, axis=0)
    img = preprocess_input(i)
    pred = np.argmax(model.predict(img), axis=1)
    return class_labels[pred[0]]





def send_email_alert(image_path,user_id):
    # Email configurations
    sender_email = 'fazalsirprojects@gmail.com'
    receiver_email = user_id
    subject = 'Wild Animal Detected!'
    body = 'A wild animal has been detected. Please check the attached image.'

    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    # Attach the image
    with open(image_path, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename= {image_path.split("/")[-1]}')
        message.attach(part)

    # Connect to the SMTP server and send the email
    try:
        smtp_server = 'smtp.gmail.com'  # Change this to your SMTP server
        smtp_port = 587  # Change this to your SMTP server port
        smtp_username = 'fazalsirprojects@gmail.com'
        smtp_password = 'bnwnqoxljugamrjd'

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        text = message.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        print('Email alert sent successfully!')
    except Exception as e:
        print(f'Error sending email alert: {e}')



