FROM python:3.8

RUN apt-get update && \
    apt-get install -y libpq-dev && \
    apt-get clean
    
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
   
COPY . .
    
CMD ["python", "bot.py"]