FROM continuumio/miniconda3

WORKDIR /app

COPY environment.yml .

RUN conda env create -f environment.yml

SHELL ["conda", "run", "-n", "GIS", "/bin/bash", "-c"]

COPY . .

EXPOSE 8501

CMD ["conda", "run", "-n", "GIS", "streamlit", "run", "app.py", "--server.address=0.0.0.0"]
