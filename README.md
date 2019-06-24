# Lasha - a simple video site
Pastime video website project written with flask a backend, project further uses some jquery and ajax as well.

# Installation
All required python packages can be installed using the "requirements.txt" file together with pip3 in one easy command.

```bash
pip3 install -r requirements.txt
```

further the database chosen behind this project is an mysql database. Login credentials can be found inside "/site/instance/config.py"

# Usage
Once all have been setup and the database initialized, one can run the website on linux with the following two commands from inside the "site" folder:

```bash
systemctl start mysql
flask run
```

Or call the bash file "main.sh" with the -s flag.

```bash
./main.sh -s
```

# Frontend

The frontend is created using various pieces modified and fitted to this project. The main theme used throughout is one called "Light Bootstrap Dashboard" by *creative tim*, template can be seen [here](https://www.creative-tim.com/product/light-bootstrap-dashboard).