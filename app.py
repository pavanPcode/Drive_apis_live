from flask import Flask, Response, stream_with_context,redirect,jsonify
from services import folders,drive_api
app = Flask(__name__)

# Register blueprints
app.register_blueprint(folders.appfolders, url_prefix='/folder')
app.register_blueprint(drive_api.appdrive, url_prefix='/images')


from services.models import URL, db ,UploadedFile

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://a50d85_payroll:p3r3nnial@MYSQL5048.site4now.net/db_a50d85_payroll'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/')
def index():
    ##
    return 'services are Up'

@app.route('/<tiny_url>')
def redirect_to_url(tiny_url):
    url = URL.query.filter_by(tiny_url=tiny_url).first_or_404()
    return redirect(url.original_url)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setting up SQLAlchemy engine and session
DATABASE_URI = app.config['SQLALCHEMY_DATABASE_URI']
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)

@app.route('/uploaded_files/<int:super_id>', methods=['GET'])
def get_uploaded_files(super_id):
    session = Session()
    try:
        # Fetch the uploaded files based on super_id
        uploaded_files = session.query(UploadedFile).filter_by(super_id=super_id).all()

        # Create a response list
        response = [
            {
                'id': file.id,
                'file_id': file.file_id,
                'file_name': file.file_name,
                'original_url': file.original_url,
                'tiny_url': f'https://googledriveapis.azurewebsites.net/{file.tiny_url}',
                'created_at': file.created_at.isoformat(),
                'description':file.description
            }
            for file in uploaded_files
        ]

        return jsonify({'status': True, 'data': response}), 200
    except Exception as e:
        return jsonify({'status': False, 'message': str(e)}), 500
    finally:
        session.close()



if __name__ == '__main__':
    app.run()
