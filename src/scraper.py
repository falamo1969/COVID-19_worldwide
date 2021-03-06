import requests
import locale
import pandas as pd
import time
from bs4 import BeautifulSoup


class CovidScraper:

    def __init__(self):
        """ Inicializa la clase CovidScraper
            Se inicializan los atributos fundamentales de la clase:
            - url_ppal: URL de la página inicial para el web scraper
            - url_base: URL de la página base donde están las páginas de los países
            - links_paises: Lista que va a contener los links de los países
            - page: HTML a tratar para obtener la información.
            - pd_confirmados: Dataframe de pandas que contiene la información relativa a contagios
            - pd_vacunados: Dataframe de pandas que contiene la información relativa a vacunas
        """
        self.url_ppal = "https://datosmacro.expansion.com/otros/coronavirus"
        self.url_base = "https://datosmacro.expansion.com"
        self.links_paises = []
        self.page = None
        self.pd_confirmados = pd.DataFrame(columns=['País', 'Fecha', 'Incremento_Muertos', 'Muertos',
                                                    'Muertos_millón', 'Incremento_Confirmados',
                                                    'Confirmados', 'Confirmados_100K_14d', ])
        self.pd_vacunados = pd.DataFrame(columns=['País', 'Fecha', 'Dosis', 'Personas_vacunadas',
                                                  'Completamente_vacunadas', '%_completamente_vacunadas'])
        locale.setlocale(locale.LC_ALL, 'nl_NL')

    def get_html(self):
        """ Lectura de la página HTML
            Se carga la información en el atributo page.
        :rtype: (int) código resultante de la lectura de la página.
        """
        self.page = requests.get(self.url_ppal)
        return self.page.status_code

    def get_links(self):
        """ Genera en el atributo de la clase links_paises la lista de links a leer, con el nombre del país
            Se carga la información en el atributo page.
        :rtype: (int) Número de países y links a tratar.
        """
        soup = BeautifulSoup(self.page.content, "html.parser")
        # Búsqueda de la tabla general de los países con los datos recientes.
        tabla = soup.find('table', attrs={'class': 'table tabledat table-striped table-condensed table-hover'})
        # Para obtener el nest dónde está la info de los nombres y enlaces
        tabla_body = tabla.find('tbody')

        # Todos los nombres de los países y enlaces a las páginas
        info_paises = tabla_body.find_all('a')

        # Lista que contiene el nombre del país y el enlace a la página que corresponde
        for info in info_paises:
            nombre = (info['title'])[0:(info['title']).find(' - COVID-19')]
            self.links_paises.append([nombre, info['href']])
        return len(self.links_paises)

    def get_vacunas_pais(self, pais, link):
        """ Lee la tabla que contiene información sobre las vacunas del país. El enlace se pasa por parámetro.
            La función acepta dos parámetros:
                'pais': Nombre del país en español del que se va a leer la información de vacunas
                'link': Sufijo a adicionar a la dirección url_base para generar la URL de la página a leer.
        """
        l_datos = []
        l_page = requests.get(self.url_base + link)
        if l_page.status_code == 200:
            # Lectura correcta de la página
            l_soup = BeautifulSoup(l_page.content, "html.parser")
            l_tabla = l_soup.find('table', attrs={'class': 'table tabledat table-striped table-condensed table-hover'})
            # Para obtener el nest dónde está la info de los nombres y enlaces
            l_tabla_body = l_tabla.find('tbody')
            rows = l_tabla_body.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                cols = [ele.text.strip() for ele in cols]
                fecha = cols[0]
                try:
                    dosis = int(locale.atof(cols[1]))
                except (ValueError, IndexError):
                    dosis = None
                try:
                    vacunadas = int(locale.atof(cols[2]))
                except (ValueError, IndexError):
                    vacunadas = None
                try:
                    completamente = int(locale.atof(cols[3]))
                except (ValueError, IndexError):
                    completamente = None
                try:
                    perc_vacunadas = locale.atof(cols[4].strip('%'))
                except (ValueError, IndexError):
                    perc_vacunadas = None
                l_datos.append([pais, fecha, dosis, vacunadas, completamente, perc_vacunadas])

            l_pd = pd.DataFrame(l_datos, columns=['País', 'Fecha', 'Dosis', 'Personas_vacunadas',
                                                  'Completamente_vacunadas', '%_completamente_vacunadas'])
            self.pd_vacunados = pd.concat([self.pd_vacunados, l_pd])
        else:
            print("Error: Vaccine data from {} not found, page: {}.".format(pais, self.url_base + link))

    def get_info_pais(self, pais_link):
        """ Lee la tabla que contiene información sobre las vacunas del país. El enlace se pasa por parámetro.
            La función acepta dos parámetros:
                'pais_link': lista que contiene el nombre país y el sufijo de la página en la que se encuentra
                             la información de los contagios
        """
        l_datos = []
        l_page = requests.get(self.url_base + pais_link[1])
        if l_page.status_code == 200:
            # Lectura correcta de la página
            l_soup = BeautifulSoup(l_page.content, "html.parser")
            l_tabla = l_soup.find('table', attrs={'class': 'table tabledat table-striped table-condensed table-hover'})
            # Para obtener el nest dónde está la info de los nombres y enlaces
            l_tabla_body = l_tabla.find('tbody')

            pais = pais_link[0]
            rows = l_tabla_body.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                cols = [ele.text.strip() for ele in cols]
                fecha = cols[0]
                try:
                    incremento = int(locale.atof(cols[1]))
                except (ValueError, IndexError):
                    incremento = None
                try:
                    muertos = int(locale.atof(cols[2]))
                except (ValueError, IndexError):
                    muertos = None
                try:
                    muertos_millon = locale.atof(cols[3])
                except (ValueError, IndexError):
                    muertos_millon = None
                try:
                    inc_confirmados = int(locale.atof(cols[4]))
                except (ValueError, IndexError):
                    inc_confirmados = None
                try:
                    confirmados = int(locale.atof(cols[5]))
                except (ValueError, IndexError):
                    confirmados = None
                try:
                    conf_100k_14d = locale.atof(cols[6])
                except (ValueError, IndexError):
                    conf_100k_14d = None
                l_datos.append([pais, fecha, incremento, muertos, muertos_millon,
                                inc_confirmados, confirmados, conf_100k_14d])

            l_pd = pd.DataFrame(l_datos, columns=['País', 'Fecha', 'Incremento_Muertos', 'Muertos',
                                                  'Muertos_millón', 'Incremento_Confirmados',
                                                  'Confirmados', 'Confirmados_100K_14d'])
            self.pd_confirmados = pd.concat([self.pd_confirmados, l_pd])

            # Búsqueda del link de la página de las vacunas del país
            l_vacunas = l_soup.find('div', attrs={'class': 'nav see-more'})
            l_li = l_vacunas.contents[1]
            l_link_vacunas = l_li.find('a')
            self.get_vacunas_pais(pais, l_link_vacunas['href'])
        else:
            print("Error: page {} not found.".format(self.url_base + pais_link[1]))

    def scrap_write_csv(self, output_csv):
        """ Escribe en formato csv la información recogida en las páginas tratadas. Toma un parámetro:
                'output_csv': Nombre del fichero output que va a recibir los datos leídos en el scraper. Los datos
                vacíos se codifican como 'NA'
        """
        # Se une la información de contagios y vacunas en el mismo dataframe para escribirlo en fichero.
        df_datos = pd.merge(self.pd_confirmados, self.pd_vacunados, on=['País', 'Fecha'], how='left')
        # Escritura del fichero, con la codificación adecuada para recoger caracteres en español. Los datos vacíos
        # se codifican como NA
        df_datos.to_csv(output_csv, encoding='latin-1', sep=',', header=True, index=False, na_rep='NA')

    def scrap_info_covid(self):
        """ Lanza el scraper de forma ordenada.
        """
        # Start timer
        start_time = time.time()

        print("Web Scraping of COVID-19 data from {}.".format(self.url_ppal))
        self.get_html()
        num_paises = self.get_links()
        print("Number of countries reported {}.".format(num_paises))

        for pais in self.links_paises:
            print("Reading data for {}".format(pais[0]))
            t1 = time.time()
            self.get_info_pais(pais)
            t2 = time.time()
            # Retrasamos las peticiones consecutivas para evitar colapso del servidor o bloqueo del scraper.
            time.sleep(10 * (t2-t1))

        # Show elapsed time
        end_time = time.time()
        print("Elapsed time: {} seconds.".format(str(round(end_time - start_time, 2))))
        print("Process complete.")
