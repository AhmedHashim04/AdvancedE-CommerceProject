ahmed@ahmed-HP-ZBook-15-G3:~$ cat ~/.ssh/id_rsa.pub
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDSX5pBVKXI9XIYW2PBZxHglJcHIKUuWGPogqEZY+cIa4nPiYfRUDDPow4tsoMxuEZeWl2eIYHWKsXPE1Gt9xnMAULI3/j6MKAGN2FtPorQYdkPtdFZybnPr1LM/yI5v0YiekNc+tXFiVbQOwUiz+ejNRTYTSQCIQO7Kj+6b+Rz2GNxx2WFh1p6H/JC6WdxmSYSdkU/YSCP+O8Dr9PAwKkCx2r+0budDwmoAnEtIpHOpUy2LbLjVUIXoCBkeGnJkQAgfHdijxCs5wz1BroeO8444Sid7uDr+OZbCd3MxCjM4Guhuq6FFNlA5qy1EC0bfOOBEEn7xwMMFwN+EzhlPA1Qc+xqMUkD8Os9JborZPTOsd6f+4+hA1+3TTQSr/iXt0ZlcNjQ2CxfYefCUghvicKBZ4Kkvwr/4iWtzHiq5Ou2/O3NFQoXOh2uoPMV2xYFq5u4v+HncWqJnUSRh1tshm0SiBod8moUaYglyH+PgciLte18Lrj254i27wCa2I3/x1ujhjOWrwO8KPTrdK/68mMfvmYaGjmcsTJt2ljR4Lp9Jx/GrR8m88rjZa+M3Rk7T6UmQuSFtHro3fDgHRgSSz3VTzC3JNie/tNwakLzpgmtBcYobI/UhTozbOgQCneWqDyVupY5Zozuh/HzsvVOTkQEeYy1E731g6yT2oHckYll7Q== ahmedha4im7@gmail.com



ssh -i ~/.ssh/id_rsa ubuntu@141.144.251.162


gcloud compute instances create my-safe-vm \
  --zone=us-central1-a \
  --machine-type=e2-small \
  --image-family=ubuntu-2404-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=10GB \
  --maintenance-policy=MIGRATE \
  --restart-on-failure


sudo apt update && sudo apt install -y curl wget ufw vim git unzip
sudo apt install -y python3 python3-pip python3-venv
sudo apt update && sudo apt install unzip -y

python3 -m venv venv
cd venv 
source bin/activate
git --version
sudo apt update
sudo apt install git

 ssh-keygen -t rsa -b 4096 -C "ahmedha4im7@gmail.com"
 cat ~/.ssh/id_rsa.pub

https://github.com/settings/keys

New SSH key
Google VPS
الـ key: لصق المفتاح اللي نسخته من cat ~/.ssh/id_rsa.pub

ssh -T git@github.com

git clone git@github.com:AhmedHashim04/railwayTest.git src

cd src
git config user.name "Ahmed Hashim"
git config user.email "ahmedha4im7@gmail.com"
cd ~/venv/src
sudo apt update
sudo apt install python3-dev build-essential -y
sudo apt install nginx -y
sudo apt install gettext
sudo apt install nano
sudo apt install -y libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libcairo2
sudo apt install -y libffi-dev libxml2 libxslt1-dev libjpeg-dev zlib1g-dev libpq-dev

sudo apt install redis
sudo apt install postgresql postgresql-contrib -y
sudo timedatectl set-timezone Africa/Cairo
sudo apt install apache2-utils
sudo apt install htop -y
sudo apt install rsync -y

pip install -r requirements.txt
sudo systemctl restart nginx
sudo systemctl reload nginx
sudo systemctl status nginx
sudo systemctl stop nginx
sudo nginx -t
sudo nginx -s reload


sudo nano /etc/nginx/sites-available/default
server {
    listen 80;
    server_name 35.246.228.81;

    client_max_body_size 50M;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias /home/ahmed/venv/src/staticfiles/;
    }

    location /media/ {
        alias /home/ahmed/venv/src/mediafiles/;
    }

    location / {
        proxy_pass http://unix:/home/ahmed/venv/src/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

sudo systemctl status redis

python manage.py collectstatic

sudo systemctl start postgresql
sudo systemctl enable postgresql
sudo systemctl status postgresql
sudo -u postgres psql
CREATE DATABASE modyexdb;
CREATE USER usermodyex WITH PASSWORD '1';
GRANT ALL PRIVILEGES ON DATABASE modyexdb TO usermodyex;
GRANT ALL PRIVILEGES ON SCHEMA public TO usermodyex;
ALTER USER usermodyex SET search_path TO public;
ALTER SCHEMA public OWNER TO usermodyex;
GRANT ALL ON SCHEMA public TO usermodyex;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO usermodyex;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO usermodyex;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO usermodyex;
GRANT ALL PRIVILEGES ON SCHEMA public TO usermodyex;
GRANT CREATE ON SCHEMA public TO usermodyex;
GRANT CREATE ON DATABASE modyexdb TO usermodyex;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO usermodyex;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO usermodyex;
ALTER USER usermodyex WITH CREATEDB;
ALTER USER usermodyex WITH SUPERUSER;
\q


python manage.py makemigrations
python manage.py migrate

python manage.py loaddata data.json

pkill gunicorn
gunicorn project.wsgi:application --bind 0.0.0.0:8000 --workers 5 --threads 2 --daemon
ps aux | grep gunicorn

sudo systemctl enable redis-server
sudo systemctl start redis-server
sudo systemctl status redis-server
redis-cli flushall  # يمسح كل الكاش


<!-- لو عايز أتأكد إن Redis هيشتغل تلقائيًا بعد الريستارت: -->
sudo systemctl is-enabled redis-server

sudo chmod o+x /home
sudo chmod o+x /home/ahmed
sudo chmod o+x /home/ahmed/venv
sudo chmod o+x /home/ahmed/venv/src
sudo chown -R www-data:www-data /home/ahmed/venv/src/staticfiles/
sudo chmod -R 755 /home/ahmed/venv/src/staticfiles/
sudo chown -R www-data:www-data /home/ahmed/venv/src/mediafiles/
sudo chmod -R 755 /home/ahmed/venv/src/mediafiles/
sudo chmod -R 777 /home/ahmed/venv/src/

sudo systemctl restart nginx
rm -rf /home/ahmed/venv/src/staticfiles/*
python manage.py collectstatic --noinput


ab -n 100 -c 10 http://35.246.228.81/ar/
pip install locust 


htop

sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

sudo nano /etc/nginx/nginx.conf
        gzip on;
         gzip_vary on; 
         gzip_proxied any;
         gzip_comp_level 6;
         gzip_buffers 16 8k;
         gzip_http_version 1.1;
         gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

sudo systemctl restart nginx
sudo systemctl status gunicorn
sudo systemctl restart gunicorn

gunicorn -w 5 -k gthread project.wsgi:application

pg_dump -U usermodyex -d modyexdb -t categories -f categories_dump.sql

psql -U usermodyex -d modyexdb -f categories_dump.sql


rsync -avz /home/ahmed/Desktop/venv/src/DATA_Backup/backup_2025-08-09_15-16/mediafiles ahmed@35.246.228.81:/home/ahmed/venv/src
