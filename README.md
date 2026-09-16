[README.md](https://github.com/user-attachments/files/32311358/README.md)
# 📊 Dashboard de Análise de E-commerce (Moda)

Aplicação Dash interativa que recria os gráficos da análise exploratória do dataset `ecommerce_estatistica.csv`.

## Gráficos disponíveis
- Histograma de Preços
- Dispersão Preço x Nota (por Gênero)
- Mapa de Calor de Correlação
- Top 10 Marcas (Barra)
- Proporção por Gênero (Pizza)
- Densidade da Nota
- Regressão Preço x Desconto

## Como rodar localmente

```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd <NOME_DO_REPOSITORIO>
pip install -r requirements.txt
python app.py
```

Depois acesse o link exibido no terminal (geralmente `http://127.0.0.1:8050`).

## Deploy (opcional)

Este app expõe a variável `server` (Flask), compatível com serviços como:
- **Render** (Web Service, comando de start: `gunicorn app:server`)
- **Heroku**
- **PythonAnywhere**

## Arquivos
- `app.py` — aplicação Dash
- `ecommerce_estatistica.csv` — dataset usado
- `requirements.txt` — dependências
