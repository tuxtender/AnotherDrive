# AnotherDrive

Client-server application for remote access to image or any files in case a Google Drive storage seems tiny. Intended to start on local machine with massive photos library to get view or share. May arrange files and folders within another directories and post comments to  shared files.

Based on previous version  of similar [application](https://github.com/tuxtender/Instatrash).
Website published [here](http://tuxtender.pythonanywhere.com/). Try "test" as login and "test12345678" as password for playing with application.

Caveats
-------
* Not tracked a disk quotation for users. Using all available memory.
* Straight implementation a temporarily archive for downloading. Multi downloading at same time not implemented. All new request for downloading zip archive will  rewrite already exists a temp archive.

## Getting Started


### Prerequisites

Python 3.8 or above

Django 2.2 or above
```
$ python -m pip install Django
```

Pillow 6.2.1 - 6.2.2 or above
```
$ python -m pip install Pillow
```


## Running the tests


### Run a views tests

Access to data. Restriction on malicious inputs. Rights on manipulation with selected items.

```
$ python .\manage.py test filestorage.tests.test_views
```

### Run a models tests

Miscellaneous ORM routines.

```
$ python .\manage.py test filestorage.tests.test_models
```

## Deployment

### Set STATIC_ROOT in settings.py
The STATIC_ROOT variable in settings.py defines the single folder you want to collect all your static files into. Typically, this would be a top-level folder inside your project, eg:

```
STATIC_ROOT = "/home/myusername/myproject/static"
# or, eg,
STATIC_ROOT = os.path.join(BASE_DIR, "static")
```
The important thing is this needs to be the full, absolute path to your static files folder.

### Run python manage.py collectstatic

```
$ python manage.py collectstatic
```

You need to re-run this command whenever you want to publish new versions of your static files.

### Create admin

```
$ python manage.py createsuperuser

```

Visit *http://yourserver/admin* to manage users.

## Built With

* [Django](https://docs.djangoproject.com/en/3.1/) - The web framework used
 

## Contributing

Pull requests are welcome. 

## Authors

* **Denis Vasilenko** - *Initial work* - [tuxtender](https://github.com/tuxtender)


## License 

[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

GNU GENERAL PUBLIC LICENSE  
Version 3, 29 June 2007

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.