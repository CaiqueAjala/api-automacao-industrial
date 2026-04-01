from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi import Form
import pandas as pd
import os

app = FastAPI()
ARQUIVO_EXCEL = "producao_extrusao.xlsx"

BOOTSTRAP_CDN = '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">'

@app.get("/", response_class=HTMLResponse)
async def home():
    return f"""
    <html>
        <head>
            {BOOTSTRAP_CDN}
            <title>Sistema de Extrusão</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
        </head>
        <body class="bg-light">
            <div class="container mt-5">
                <div class="card shadow">
                    <div class="card-header bg-primary text-white">
                        <h2 class="mb-0">Relatório de Extrusão</h2>
                    </div>
                    <div class="card-body">
                        <form action="/registrar" method="post">
                            <div class="mb-3">
                                <label class="form-label">Operador:</label>
                                <input type="text" name="operador" class="form-control" required>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">Extrusora:</label>
                                <select name="extrusora" class="form-select">
                                    <option value="Extrusora A">Extrusora A</option>
                                    <option value="Extrusora B">Extrusora B</option>
                                    <option value="Extrusora C">Extrusora C</option>
                                </select>
                            </div>

                            <div class="mb-3">
                                <label class="form-label">Peso Bruto (kg):</label>
                                <input type="number" step="0.01" name="peso_bruto" class="form-control" required>
                            </div>

                            <button type="submit" class="btn btn-success w-100">Salvar no Excel ✅</button>
                        </form>
                        <hr>
                        <a href="/dashboard" class="btn btn-outline-secondary w-100">Ver Dashboard 📊</a>
                    </div>
                </div>
            </div>
        </body>
    </html>
    """
@app.post("/registrar")
async def registrar_producao(operador: str = Form(...),extrusora: str = Form(...), material: str = Form(...), peso_bruto: float = Form(...)):
    data = {"Operador": operador, "Extrusora": extrusora, "Material": material, "Peso Bruto": peso_bruto}
    df_novo = pd.DataFrame([data])

    # Se o arquivo não existir, cria um novo. Se existir, anexa sem apagar o anterior.
    if not os.path.exists(ARQUIVO_EXCEL):
        df_novo.to_excel(ARQUIVO_EXCEL, index=False)
    else:
        df_antigo = pd.read_excel(ARQUIVO_EXCEL)
        df_final = pd.concat([df_antigo, df_novo], ignore_index=True)
        df_final.to_excel(ARQUIVO_EXCEL, index=False)
            
    return {"message": "Dados salvos com sucesso no Excel!"}


@app.get("/dashboard", response_class=HTMLResponse)
async def visualizar_producao():
    if os.path.exists(ARQUIVO_EXCEL):
        df = pd.read_excel(ARQUIVO_EXCEL)

        total_kg = df["Peso Bruto"].sum()

        producao_por_maquina = df.groupby("Extrusora")["Peso Bruto"].sum().to_dict()

        #lista visual para as máquinas:
        maquinas = "".join ([f"<li>{maq}: {peso}: kg </li>" for maq, peso in producao_por_maquina.items()])
        return f"""
        <html>
            <head>
                {BOOTSTRAP_CDN}
                <meta name="viewport" content="width=device-width, initial-scale=1">
            </head>
            <body class="bg-light">
                <div class="container mt-4">
                    <div class="card shadow border-0">
                        <div class="card-header bg-dark text-white d-flex justify-content-between align-items-center">
                            <h3 class="mb-0">Painel de Produção</h3>
                            <span class="badge bg-success">Total: {df['Peso Bruto'].sum():.2f} kg</span>
                        </div>
                        <div class="card-body">
                            <table class="table table-hover mt-3">
                                <thead class="table-light">
                                    <tr>
                                        <th>Máquina</th>
                                        <th class="text-end">Total Produzido</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {maquinas}
                                </tbody>
                            </table>
                            <div class="d-grid gap-2 mt-4">
                                <a href="/" class="btn btn-primary">Fazer Novo Registro</a>
                            </div>
                        </div>
                    </div>
                </div>
            </body>
        </html>
        """
    