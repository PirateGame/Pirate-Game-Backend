FROM python:3
ADD analyse.py /
ADD events.py /
ADD grid.py /
ADD looper.py /
ADD main.py /
ADD nameFilter.py /

RUN pip install -r requirements.txt 

CMD ["python", "./main.py"]