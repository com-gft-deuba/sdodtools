# Prepare
python3 -m pip install --upgrade pip setuptools wheel build virtualenv

# Build
python3 -m build --sdist .

# Install
python3 -m pip install --user --force-reinstall dist/sdodtools_briconaut-0.0.1.tar.gz 
