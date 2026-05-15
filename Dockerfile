FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV FLASK_APP=Registro_de_pedidos/app.py
ENV FLASK_DEBUG=1
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]