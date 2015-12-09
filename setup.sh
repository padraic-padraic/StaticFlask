pyvenv venv
source venv/bin/activate
pip3 install -r requirements.txt
git clone https://github.com/google/py-gfm
cd py-gfm
python3 setup.py build && python3 setup.py install
cd ../StaticFlask
python3 freeze.py
echo 'Now edit your default apache/nginx conf to point to /var/www/Static'
