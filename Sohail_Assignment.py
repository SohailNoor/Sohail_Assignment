from flask import Flask, render_template,request
import boto3
from flask_mysqldb import MySQL
from PIL import Image
import glob
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')
#
# rds_client = boto3.client('rds')
# response = rds_client.describe_db_instances(
#     DBInstanceIdentifier='Sohail-db',
# )
#
# host = response['DBInstances'][0]['Endpoint']['Address']
# port = response['DBInstances'][0]['Endpoint']['Port']
# username = response['DBInstances'][0]['MasterUsername']
# PASSWORD = "12345678"
#
# path = "/home/krishna/PycharmProjects/Sohail_Assignment/static/images/post/"
# pre_images_list = glob.glob("/home/krishna/PycharmProjects/Sohail_Assignment/static/images/pre/*")
# post_images_list = glob.glob("/home/krishna/PycharmProjects/Sohail_Assignment/static/images/post/*")
# for image in pre_images_list:
#     image_file = Image.open(image)
#     image_file = image_file.convert('1')
#     image = image.split("/")
#     image_file.save(path + image[-1])
#
# post_images_list = glob.glob("/home/krishna/PycharmProjects/Sohail_Assignment/static/images/post/*")
# for i in pre_images_list:
#     s3_resource.meta.client.upload_file(i, 'pre-processed-kc', i.split("/")[-1])
#
# for i in post_images_list:
#     s3_resource.meta.client.upload_file(i, 'post-porcessed-kc', i.split("/")[-1])

@app.route('/')
def index():

    return render_template('mnoormuh_index.html')

@app.route('/gallery')
def gallery():
    pre_response = s3_client.list_objects(
        Bucket='pre-processed-kc'
    )

    post_response = s3_client.list_objects(
        Bucket='post-porcessed-kc'
    )
    pre_response_list = []
    for i in pre_response['Contents']:
        pre_response_list.append(i['Key'])

    post_response_list = []
    for i in post_response['Contents']:
        post_response_list.append(i['Key'])

    j = 1
    k = 1
    pre_paths = []
    post_paths = []

    for i in pre_response_list:
        i_spl = i.split(".")
        s3_resource.meta.client.download_file('pre-processed-kc', i, "/home/krishna/PycharmProjects/Sohail_Assignment/static/images/pre/" +
                                               "{}.{}".format(j,i_spl[1]))
        pre_paths.append("static/images/pre/" +"{}.{}".format(j,i_spl[1]))
        j += 1

    for i in post_response_list:
        i_spl = i.split(".")
        s3_resource.meta.client.download_file('post-porcessed-kc', i,"/home/krishna/PycharmProjects/Sohail_Assignment/static/images/post/" +
                                               "{}.{}".format(k,i_spl[1]))
        post_paths.append("static/images/post/" + "{}.{}".format(k, i_spl[1]))
        k += 1

    return render_template('mnoormuh_pg2.html',pre_list=pre_paths,post_list=post_paths)

@app.route('/submit')
def submit():
    return render_template("mnoormuh_pg4.html")


@app.route('/upload_data', methods=['POST'])
def upload():
    email = request.form['email']
    phone = request.form['Phone']
    image = request.form['file']

    pre_image_name = image.split("/")[-1]
    s3_resource.meta.client.upload_file(image, 'pre-processed-kc', pre_image_name)
    image_file = Image.open(image)
    image_file = image_file.convert('1')

    #Change krishna to ubuntu
    post_image_name = "post_" + pre_image_name
    image_file.save("/home/krishna/" + post_image_name)
    s3_resource.meta.client.upload_file(image, 'post-porcessed-kc', pre_image_name)


    return image

if __name__ == '__main__':
    app.run(debug=True)
