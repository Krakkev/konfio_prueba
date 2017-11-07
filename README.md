# PRUEBA KONFÍO

## Requerimientos
* python 2.7
* pandas
* python-pip
* Flask
* SQLAlchemy
* python-bsddb3
* libdb5.3
* scrapy-deltafetch
* pip install requests (Para pruebas)
* pip install IPython==5.0 (Para pruebas)

Para instalar los requerimientos puede ejecutar desde la consola el archivo setup.sh situado en la raíz de este repositorio de la siguiente forma: 

* $```chmod +x setup.sh```
* $```sudo ./setup.sh```

*** Esto también creara la base de datos que se usara en la aplicación ***


## ¿Cómo ejecutar el projecto?

Seguir los siguientes pasos:
      
1.  Posicionarte dentro de la carpeta konfio
    ```konfio_prueba/konfio/ ```          
        
2.  Declarar la variable de entorno FLASK_APP
    $```export FLASK_APP=konfio.py ``` 
3.  Correr la aplicacion de flask
    $```flask run```
    
    
## ¿Cómo utilizar la API?

### Modo gráfico:

1. Entrar con un navegador a la siguiente url -> http://127.0.0.1:5000/sources/
2. Elegir el sitio del cual quiere conseguir información. 
3. Ingresar el número de anuncios que desea obtener. (Mínimo 2)
4. Presionar el botón que dice "Crawl!"
5. Esperar unos segundos mientras se obtiene la información
6. Se muestra el json obtenido con tú busqueda 
    * Los anuncios obtenidos se guardan en la base de datos localizada en: ```/konfio_prueba/konfio/entregable/konfio.db```
    * El json generado se guarda en:  ```/konfio_prueba/konfio/ads.json```
    
### Modo consola:      
1. En una nueva consola ingresar a ipython
    $ ```ipython```
2. Importar la libreria requests
   ```import requests```
3. Definir el sitio y el número de anuncios que se quieren
    ```
    data = {
        "site": "mercadolibre", #mercadolibre puede cambiarse por alguno de los sitios
        "ads": "5" # 5 puede cambiarse por la cantidad de anuncios deseada
    }
    ```
4. Enviar request usando metodo POST con los parámetros previamente definidos
   ```r = requests.post('http://127.0.0.1:5000/products/', data=data)```
    * Los anuncios obtenidos se guardan en la base de datos localizada en: ```/konfio_prueba/konfio/entregable/konfio.db```
    * El json generado se guarda en:  ```/konfio_prueba/konfio/ads.json```
5. Almacenar el json en una variable para un uso posterior
    ```json_anuncios = r.json()```


## Entregable
En la carpeta  ```konfio_prueba/konfio/entregable``` se encuentra en archivo llamado  ```konfio.db```
el cual es una base de datos que contiene una tabla llamada items con los campos:
    - id_item
    - price
    - title
    - description
    - site
en la cual se almacena cada uno de los items entregados por las busquedas.

## Notas
Se utiliza el framework llamado scrapy y se utiliza el parámetro CLOSESPIDER_ITEMCOUNT para determinar el número de items
que se obtienen al realizar la búsqueda. El mínimo de items obtenibles es 2, pues cuando el framework detecta que se llegó
en el siguiente request.

Para asegurar que no se repita la inserción de un item repetido se utiliza Deltafetch, el cual es un archivo que almacena los identificadores de cada item y la fecha en la que fue hecho el request. Gracias a este archivo al momento de hacer el crawleo de la pagina se pueden omitir los request de los items previamente almacenados.

Los sitios crawleados fueron century21, mercadolibre e inmuebles24. Los tres son sitios para ventas o rentas de inmuebles.
Para los tres sitios se usaron regular expressions y xpaths para acceder a los atributos. Para mercadolibre también se hicieron peticiones a su API (pública).

Los tres spiders cuentan con la estructura necesaria para navegar por todo el sitio (incluyendo la paginación) y los settings están preparados para hacer un recorrido no invasivo.

Para el control más exacto del numero de items por busqueda se redujo el numero de requests simultaneos a 1, por lo que la obtención de los items no será en paralelo.
