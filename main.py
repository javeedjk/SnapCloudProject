import os
from flask import Flask, redirect, request, Response
import io
import boto3

app = Flask(__name__)

s3_client = boto3.client(
    's3',
    aws_access_key_id=os.environ.get("ACCESS_KEY"),
    aws_secret_access_key=os.environ.get("SECRET_KEY"),
    region_name='us-east-1'
)

@app.route("/")
def homepage():
    images_in_s3 = list_s3_object_names('snapcloud-jk', '')
    index_html = f"""
    <body>
        <h1 align='center'>Snap Cloud</h1>
        <hr/><hr/>
        <form action="/upload" method="post" enctype="multipart/form-data">
        <table align = 'center'>
            <tr>
                <td>Select a image</td>
                <td><input type="file" name="image" accept="image/**" required></td>
            </tr>
            <tr>
                <td colspan = 2 align = 'center'> <input type='submit' value='upload'</td>
            </tr>
        </table>
    </form>
     <h2 align='center'>Avaiable Items </h2>
    <ul align='center'>
    """
    for image in images_in_s3:
        index_html += f'<li><a href="/files/{image}">{image}</a></li>'
    index_html += '''</ul>
    </body>'''
    return index_html

@app.route('/upload', methods=["POST"])
def upload_image():
    file = request.files['image']
    file.save(os.path.join('',file.filename))
    file_path= os.getcwd() + '/' + file.filename
    print(file_path)
    bucket_name = 'snapcloud-jk'
    filename= file.filename
    output = upload_file_to_s3(file_path, bucket_name, filename)
    os.remove(file.filename)
    return redirect("/")

@app.route('/files/<filename>')
def display_file(filename):
    return f"""
        <br/>
    <body>
    <div style="background: radial-gradient(black, transparent); padding: 50px; 
                                border-radius: 120px; margin-left: 100px; margin-right: 100px;">
        <a href="/" style="padding: 50px;">Back to Home Page</a>
    <br/>
        <center >
            <h2>{filename}</h2>
            <img src="/images/{filename}" width='60%'>
        </center>
    </div>
    </body>
    """

@app.route('/images/<imagename>')
def getfile(imagename):
    image_bytes = fetch_s3_file_as_bytes('snapcloud-jk', imagename)
    return Response(io.BytesIO(image_bytes), mimetype='image/jpeg')


def upload_file_to_s3(file_path, bucket_name, filename):
    response = s3_client.upload_file(file_path, bucket_name, filename)
    return True

def list_s3_object_names(bucket_name, prefix=''):
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    object_names = []
    if 'Contents' in response:
        for obj in response['Contents']:
            object_names.append(obj['Key'])
    return object_names

def fetch_s3_file_as_bytes(bucket_name, object_name):
    response = s3_client.get_object(Bucket=bucket_name, Key=object_name)
    file_content = response['Body'].read()
    return file_content

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
