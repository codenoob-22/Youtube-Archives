# Youtube-Archives

What this project does -  
  A basic app that fetches video details of latest videos for given search query
  from YouTube API and store them into database. This should run continuously in
  Some given time interval. 
  

tech stack used-
```
Python==3.7
Django==3.1.3
```

create a virtual-environment using virtualenv or pyenv or python itself
```
python3.7 -m venv env
source env/bin/activate
```
to run server use command
```
python manage.py runserver
```
currently there is no dashboard, you can try adding query param *search_query* to make the search query
```
localhost:8000/video_store/search/?search_query= want good
```

For docker file you would need to build image,
Sorry, this was my first time with docker so have a very basic docker setup.
```
# do this within the repository.
sudo docker build -t fam_backend .

sudo docker run -p 8000:8000 fam_backend

```
