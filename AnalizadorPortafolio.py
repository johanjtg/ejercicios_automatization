import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime


class AnalizadorPortafolio:
    """Clase para analizar y reportar portafolio de acciones"""

    def __init__(self, tickers, cantidades):
        """
        Args:
            tickers (list): Lista de simbolos ['AAPL', 'GOOGL', etc.]
            cantidades (list): Numero de acciones de cada una [10, 5, etc.]
        """
        self.tickers = tickers
        self.cantidades = cantidades
        self.datos = None

    def obtener_datos(self, periodo='1mo'):
        """Obtener datos historicos de todas las acciones"""
        datos_lista = []

        for ticker, cantidad in zip(self.tickers, self.cantidades):
            accion = yf.Ticker(ticker)
            hist = accion.history(period=periodo)

            precio_actual = hist['Close'].iloc[-1]
            precio_anterior = hist['Close'].iloc[-2]
            cambio_diario = ((precio_actual - precio_anterior) / precio_anterior) * 100

            datos_lista.append({
                'Ticker': ticker,
                'Cantidad': cantidad,
                'Precio': precio_actual,
                'Valor Total': precio_actual * cantidad,
                'Cambio %': cambio_diario,
                'Ganancia/Perdida $': (precio_actual - precio_anterior) * cantidad
            })

        self.datos = pd.DataFrame(datos_lista)
        return self.datos

    def generar_resumen(self):
        """Generar resumen estadistico del portafolio"""
        valor_total = self.datos['Valor Total'].sum()
        cambio_total = self.datos['Ganancia/Perdida $'].sum()
        cambio_porcentaje = (cambio_total / (valor_total - cambio_total)) * 100

        resumen = f"""
REPORTE DIARIO DE PORTAFOLIO - {datetime.now().strftime('%Y-%m-%d')}
{'=' * 60}

Valor Total del Portafolio: ${valor_total:,.2f}
Cambio del Dia: ${cambio_total:,.2f} ({cambio_porcentaje:+.2f}%)

{'MEJOR' if cambio_total > 0 else 'PEOR'} RENDIMIENTO DEL DIA:
{self.datos.nlargest(1, 'Cambio %')[['Ticker', 'Cambio %', 'Ganancia/Perdida $']].to_string(index=False)}

DESGLOSE POR ACCION:
{self.datos.to_string(index=False)}
        """
        return resumen

    def crear_grafico(self, filename='portafolio.png'):
        """Crear grafico visual del portafolio"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        ax1.pie(self.datos['Valor Total'], labels=self.datos['Ticker'],
                autopct='%1.1f%%', startangle=90)
        ax1.set_title('Distribucion del Portafolio')

        colors = ['green' if x > 0 else 'red' for x in self.datos['Cambio %']]
        ax2.barh(self.datos['Ticker'], self.datos['Cambio %'], color=colors)
        ax2.set_xlabel('Cambio %')
        ax2.set_title('Rendimiento Diario')
        ax2.axvline(x=0, color='black', linestyle='-', linewidth=0.5)

        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()

        return filename

    def guardar_historial(self, filename='historial_portafolio.csv'):
        """Guardar datos en CSV para analisis historico"""
        self.datos['Fecha'] = datetime.now().strftime('%Y-%m-%d')

        try:
            df_existente = pd.read_csv(filename)
            df_nuevo = pd.concat([df_existente, self.datos], ignore_index=True)
            df_nuevo.to_csv(filename, index=False)
        except FileNotFoundError:
            self.datos.to_csv(filename, index=False)

        print(f"Historial guardado en {filename}")
