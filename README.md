# konfio_prueba
Este repositorio contiene el projecto solicitado para la pruba de konfio.


# Requerimientos
El projecto requiere python2.7 y sus siguientes librerias:
    - scrapy
      sudo pip install scrapy
    - pandas
      sudo pip install pandas
    - sqlalchemy 
      sudo pip install SQLAlchemy
    - deltafetch
      sudo pip install scrapy-deltafetch
    - requests
      sudo pip install requests
    - flask
      sudo pip install Flask
      
 
# Ejecucion
1. $cd konfio_prueba/konfio/          #............ Posicionarte dentro de la carpeta konfio
2. $python setup.py                   #............ Correr setup.py para crear la base de datos
3. $export FLASK_APP=konfio.py        #............ Declarar la variable de entorno FLASK_APP
4. $flask run                         #............ Correr la aplicacion de flask
5. http://127.0.0.1:5000/sources/     ............ Ir a la url donde esta corriendo la app
6. Elegir el sitio a crawlear e ingresar el numero de items que se desean obtener (default 10). 
7. Presionar el boton de Crawl! para comenzar la busqueda de los items
8. Se muestra el json obtenido con tu busqueda http://127.0.0.1:5000/products/ 

"El proyecto corre al 100%, si esto no ocurre favor de instalar librerias faltantes"

# Entregable
En la carpeta konfio_prueba/konfio/entregable se encuentra en archivo llamado "konfio.db"
el cual es una base de datos que contiene una tabla llamada items con los campos:
    - id_item
    - price
    - title
    - description
    - site
en la cual se almacena cada uno de los items entregados por las busquedas.

# Notas
Se utiliza el framework llamdo scrapy y se utiliza el parametro CLOSESPIDER_ITEMCOUNT para determinar el numero de items
que se obtienen al realizar la busqueda. El minimo de items obtenibles es 2, pues cuando el framework detecta que se llego
al numero de items deseado ya se esta ejecutando un ultimo request.

Para asegurar que no se repita la insercion de un item repetido se utiliza Deltafetch el cual es un archivo que almacena los identificadores de cada item y la fecha en la que fue hecho el request. Gracias a este archivo al momento de hacer el crawleo de la pagina se pueden omitir los request de los items previamente almacenados.

Los sitios crawleados fueron century21, mercadolibre e inmuebles24. Los tres son sitios para ventas o rentas de inmuebles.
Para los tres sitios se utilizaron regular expressions y xpaths para acceder a los atributos. Para mercadolibre tambien se hicieron peticiones a su api (publico).

Los tres spiders cuentan con la estructura necesaria para navegar por todo el sitio (incluyendo la paginacion) y los settings estan preparados para hacer un recorrido no invasivo.

Para el control mas exacto del numero de items por busqueda se redujo el numero de requests simultaneos a 1, por lo que la obtencion de los items no sera en paralelo.



