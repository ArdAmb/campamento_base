# Campamento Base
Receptor de datos en Rpi

# Instalacion
```
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
```

# Servidor
```
python manage.py runserver 0.0.0.0:8000
```

# Controlador por Telegram
```
python manage.py remote_control
```
