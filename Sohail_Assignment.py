from flask import Flask, render_template,request
import boto3
import MySQLdb
from PIL import Image
import os

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "/"
s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')

client = boto3.client('rds')
response = client.describe_db_instances(
        DBInstanceIdentifier='Sohail-db',
    )

username = response['DBInstances'][0]['MasterUsername']
endpoint = response['DBInstances'][0]['Endpoint']['Address']
db_conn = MySQLdb.connect(endpoint,username,"12345678","sys")

cursor = db_conn.cursor()

@app.route('/')
def index():

    return render_template('mnoormuh_index.html')

@app.route('/gallery')
def gallery():
    pre_paths = []
    post_paths = []
    cursor.execute("SELECT s3_raw_url FROM records ")
    result = cursor.fetchall()
    for r in result:
        pre_paths.append(r[0])

    cursor.execute("SELECT s3_finished_url FROM records ")
    result = cursor.fetchall()
    for r2 in result:
        pre_paths.append(r2[0])
    return render_template('mnoormuh_pg2.html',pre_list=pre_paths,post_list=post_paths)

@app.route('/submit')
def submit():
    return render_template("mnoormuh_pg4.html")


@app.route('/upload_data', methods=['GET', 'POST'])
def upload():
    email = request.form['email']
    phone = request.form['Phone']
    image = request.files['file']

    cursor.execute("DROP TABLE IF EXISTS records")
    sql_command = """CREATE TABLE records (id INTEGER AUTO_INCREMENT PRIMARY KEY,email VARCHAR(32),phone VARCHAR(32),s3_raw_url VARCHAR(100),s3_finished_url VARCHAR(100),status INT(1));"""
    cursor.execute(sql_command)


    img_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
    image.save(img_path)

    s3_resource.meta.client.upload_file(img_path, 'pre-processed', image.filename)
    image_file = Image.open(image)
    image_file = image_file.convert('1')
    url_pre = s3_client.generate_presigned_url('get_object', Params={'Bucket': 'pre-processed', 'Key': image.filename},
                                        ExpiresIn=3600)

    post_image_name = "post_" + image.filename
    post_image_path = app.config['UPLOAD_FOLDER'] + post_image_name
    image_file.save(app.config['UPLOAD_FOLDER'] + post_image_name)
    s3_resource.meta.client.upload_file(post_image_path, 'post-porcessed-kc', post_image_name)

    url_post = s3_client.generate_presigned_url('get_object',
                                               Params={'Bucket': 'post-processed', 'Key': post_image_name},
                                               ExpiresIn=3600)

    if url_post is not None:
        status = 1
    else:
        status = 0

    format_str = """INSERT INTO records ( email, phone, s3_raw_url, s3_finished_url, status) VALUES ("{email1}", "{phone1}", "{s3_raw_url1}", "{s3_finished_url1}", "{status1}");"""
    sql_command = format_str.format(email1=email, phone1=phone, s3_raw_url1=url_pre, s3_finished_url1=url_post,
                                    status1=status)

    cursor.execute(sql_command)
    db_conn.commit()


    return "Success"

if __name__ == '__main__':
    app.run(debug=True)