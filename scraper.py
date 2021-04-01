import requests
import locale
import pandas as pd
import time
from bs4 import BeautifulSoup


class CovidScraper:

    def __init__(self):
        self.url_ppal = "https://datosmacro.expansion.com/otros/coronavirus"
        self.url_base = "https://datosmacro.expansion.com"
        self.datos = []
        self.links_paises = []
        self.page = None
        locale.setlocale(locale.LC_ALL, 'nl_NL')

    def get_html(self):
        self.page = requests.get(self.url_ppal)
        return self.page.status_code

    def get_links(self):
        soup = BeautifulSoup(self.page.content, "html.parser")
        # Busqueda de la tabla general de los países con los datos recientes.
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

    def get_info_pais(self, pais_link):
        l_datos = []
        l_page = requests.get(self.url_base + pais_link[1])
        l_soup = BeautifulSoup(l_page.content, "html.parser")
        l_tabla = l_soup.find('table', attrs={'class': 'table tabledat table-striped table-condensed table-hover'})
        # Para obtener el nest dónde está la info de los nombres y enlaces
        l_tabla_body = l_tabla.find('tbody')

        rows = l_tabla_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            pais = pais_link[0]
            fecha = cols[0]
            try:
                incremento = int(locale.atof(cols[1]))
            except (ValueError, IndexError):
                incremento = 0
            try:
                muertos = int(locale.atof(cols[2]))
            except (ValueError, IndexError):
                muertos = 0
            try:
                muertos_millon = locale.atof(cols[3])
            except (ValueError, IndexError):
                muertos_millon = 0.0
            try:
                inc_confirmados = int(locale.atof(cols[4]))
            except (ValueError, IndexError):
                inc_confirmados = 0
            try:
                confirmados = int(locale.atof(cols[5]))
            except (ValueError, IndexError):
                confirmados = 0
            try:
                conf_100k_14d = locale.atof(cols[6])
            except (ValueError, IndexError):
                conf_100k_14d = 0.0
            l_datos.append([pais, fecha, incremento, muertos, muertos_millon,
                            inc_confirmados, confirmados, conf_100k_14d])
        return l_datos

    def scrap_write_csv(self, output_csv):
        df_datos = pd.DataFrame(self.datos, columns=['País', 'Fecha', 'Incremento_Muertos', 'Muertos',
                                                     'Muertos_millón', 'Incremento_Confirmados',
                                                     'Confirmados', 'Confirmados_100K_14d'])

        df_datos.to_csv(output_csv, encoding='latin-1', sep=',', header=True)

    def scrap_info_covid(self):
        # Start timer
        start_time = time.time()

        print("Web Scraping of COVID-19 data from {}.".format(self.url_ppal))
        self.get_html()
        num_paises = self.get_links()
        print("Number of countries reported {}.".format(num_paises))

        for pais in self.links_paises:
            print("Reading data for {}".format(pais[0]))
            self.datos += self.get_info_pais(pais)

        # Show elapsed time
        end_time = time.time()
        print("Elapsed time: {} seconds.".format(str(round(end_time - start_time, 2))))
        print("Process complete.")
