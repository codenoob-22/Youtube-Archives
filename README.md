# Youtube-Archives

## What this project does -  
  A basic app that fetches video details of latest videos for given search query
  from YouTube API and store them into database. This should run continuously in
  Some given time interval. 
  

tech stack used-
```
Python==3.7
Django==3.1.3
```
## Instructions-  
  
create a virtual-environment using virtualenv or pyenv or python itself
```
python3.7 -m venv env
source env/bin/activate
pip install -r requirements.txt
```
to run server use command
```
#adds the cronjobs - made them to run every five minutes for now
python manage.py crontab add
#removes the cronjobs- in case you want to stop it
python manage.py crontab remove
#runs the server
python manage.py runserver
```
currently there is no dashboard, but there is a little hack, you can visit this link to get a search bar along with results in bottom
```
localhost:8000/video_store/search/
```
submit API keys on url -
```
localhost:8000/video_store/youtube_keys/
```

For docker file you would need to build image,
Sorry, this was my first time with docker so have a very basic docker setup.
```
# do this within the repository.
sudo docker build -t fam_backend .
#run this command for the image name you find
sudo docker run -p 8000:8000 fam_backend:latest

```
## testing-  

for testing cronjobs you can check debug.log in logs folder
for testing api you can visit this url after starting server
```
localhost:8000/video_store/search/
```

## Bonus Points-  
1) manages multiple keys.
2) has a dashboard( kind of :|) where you can put and view search results.
3) has flexible search query api.
4) this app also has jupyter notebook extension installed 
you can use it by using 
```
 python manage.py shell_plus --notebook
```
NOTE- use-
```
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
```
To run functionalities normaly on jupyter notebook
