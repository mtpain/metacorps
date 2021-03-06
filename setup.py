from distutils.core import setup


required_packages = [
    'click==6.6',
    'Flask==0.11.1',
    'Flask-Cors==3.0.3',
    'Flask-Login==0.3.2',
    'Flask-Mail==0.9.1',
    'flask-mongoengine==0.8',
    'Flask-Principal==0.4.0',
    'Flask-Security==1.7.5',
    'Flask-WTF==0.13.1',
    'gensim==3.0.1',
    'html5lib==0.9999999',
    'Jinja2==2.8',
    'lxml==3.8.0',
    'matplotlib==2.1.1',
    'mccabe==0.6.1',
    'mistune==0.7.4',
    'mongoengine==0.10.7',
    'mpmath==1.0.0',
    'networkx==2.0',
    'nltk==3.2.4',
    'nose==1.3.7',
    'notebook==5.0.0',
    'numpy==1.14.0',
    'openpyxl==2.4.8',
    'packaging==16.8',
    'pandas==0.22.0',
    'pandocfilters==1.4.2',
    'parso==0.1.1',
    'passlib==1.7.0',
    'pexpect==4.3.1',
    'pickleshare==0.7.4',
    'prompt-toolkit==1.0.15',
    'protobuf==3.4.0',
    'ptyprocess==0.5.2',
    'pycaption==1.0.0',
    'pycodestyle==2.3.1',
    'pydot==1.2.3',
    'pyflakes==1.6.0',
    'Pygments==2.2.0',
    'pymongo==3.4.0',
    'pyparsing==2.2.0',
    'python-dateutil==2.6.1',
    'pytz==2017.3',
    'pyzmq==16.0.2',
    'qtconsole==4.3.1',
    'requests==2.13.0',
    'responses==0.7.0',
    'rpy2==2.9.0',
    'scikit-learn==0.19.1',
    'scipy==0.19.1',
    'seaborn==0.8.1',
    'sklearn==0.0',
    'terminado==0.6',
    'testpath==0.3.1',
    'tornado==4.5.2',
    'virtualenv==15.1.0',
    'wcwidth==0.1.7',
    'webencodings==0.5.1',
    'Werkzeug==0.11.11',
    'widgetsnbextension==3.0.2',
    'wrapt==1.10.11',
    'WTForms==2.1',
    'xlrd==1.1.0'
]

setup(
    name='Metacorps',
    version='0.1',
    description='Web app for managing and annotating metaphor data',
    author='Matthew Turner',
    author_email='maturner01@gmail.com',
    install_requires=required_packages,
    data_files=['app/conf/default.cfg'],
    packages=['projects', 'projects.common', 'projects.viomet', 'app']
)
