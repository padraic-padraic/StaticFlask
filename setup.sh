pyvenv venv
source venv/bin/activate
pip3 install -r requirements.txt
git clone https://github.com/mitya57/python-markdown-math
cd python-markdown-math
python3 setup.py build && python3 setup.py install
cd ../StaticFlask
python3 __init__.py