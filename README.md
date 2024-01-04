python3.11

#create virtial env 
pip install --upgrade virtualenv
virtualenv -p python3 envname
#activate env
source/envname/bin/activate

git clone 



Install dependencies:
pip install -r requirements.txt


Create a development database:
./manage.py migrate


If everything is alright, you should be able to start the Django development server:
./manage.py runserver
