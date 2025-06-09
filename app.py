import web
import pandas as pd
import numpy as np
import io
import os

urls = (
    '/', 'Index',
    '/upload', 'Upload',
    '/action', 'Action',
)

render = web.template.render('templates/')

# Variable global para almacenar el DataFrame
df_global = None

class Index:
    def GET(self):
        return render.index()

class Upload:
    def POST(self):
        global df_global
        x = web.input(myfile={})
        file = x['myfile']

        if not file.filename.endswith('.csv'):
            return "Solo se permiten archivos CSV"

        # Crear carpeta 'uploads' si no existe
        if not os.path.exists("uploads"):
            os.makedirs("uploads")

        # Guardar el archivo en la carpeta 'uploads'
        filepath = os.path.join("uploads", file.filename)
        with open(filepath, "wb") as f:
            f.write(file.file.read())

        # Leer el CSV desde el archivo guardado
        df_global = pd.read_csv(filepath)

        return render.actions()

class Action:
    def GET(self):
        return render.actions()

    def POST(self):
        global df_global
        if df_global is None:
            return "Primero sube un archivo CSV"

        i = web.input()
        action = i.get('action')
        n = i.get('n')
        col = i.get('col')
        valor = i.get('valor')
        op = i.get('op')  # operador para filtro

        output = ""

        if action == 'head':
            n = int(n) if n else 5
            output = df_global.head(n).to_html()
        elif action == 'tail':
            n = int(n) if n else 5
            output = df_global.tail(n).to_html()
        elif action == 'info':
            buffer = io.StringIO()
            df_global.info(buf=buffer)
            output = "<pre>" + buffer.getvalue() + "</pre>"
        elif action == 'describe':
            output = df_global.describe().to_html()
        elif action == 'shape':
            output = f"Filas: {df_global.shape[0]}, Columnas: {df_global.shape[1]}"
        elif action == 'columns':
            output = ", ".join(df_global.columns)
        elif action == 'select_one':
            if col in df_global.columns:
                output = df_global[col].to_frame().to_html()
            else:
                output = "Columna no existe"
        elif action == 'select_multi':
            if col:
                cols = [c.strip() for c in col.split(',')]
                if all(c in df_global.columns for c in cols):
                    output = df_global[cols].to_html()
                else:
                    output = "Alguna columna no existe"
            else:
                output = "No se especificaron columnas"
        elif action == 'filter':
            if col in df_global.columns and valor and op:
                try:
                    val_num = float(valor)
                    columnas_validas = ['nombre', 'matricula', col]
                    columnas_validas = [c for c in columnas_validas if c in df_global.columns]

                    if op == '>':
                        filtro = np.greater(df_global[col], val_num)
                    elif op == '<':
                        filtro = np.less(df_global[col], val_num)
                    elif op == '==':
                        filtro = np.equal(df_global[col], val_num)
                    else:
                        return "Operador no válido. Usa <, > o =="

                    filtered = df_global.loc[filtro, columnas_validas]
                    output = filtered.to_html()
                except ValueError:
                    return "El valor para filtrar debe ser numérico."
            else:
                output = "Parámetros inválidos para filtrar"
        else:
            output = "Acción no válida"

        return render.result(output)

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
