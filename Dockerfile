# Use an official Python runtime as the base image
FROM python:3.10-alpine

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

RUN pip install telebot

# Defina o comando para executar o programa
CMD ["python", "main.py"]
