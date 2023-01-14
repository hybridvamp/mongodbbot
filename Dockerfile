FROM python:3.9

# create app directory
RUN mkdir /app
WORKDIR /app

# copy requirements
COPY requirements.txt .

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy the rest of the code
COPY . .

# run the script
CMD ["python", "main.py"]
