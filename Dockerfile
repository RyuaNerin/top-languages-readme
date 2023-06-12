FROM python:3.7

# Install dependencies.
ADD requirements.txt /requirements.txt
ADD main.py /main.py
ADD options.py /options.py
RUN pip install -r requirements.txt

CMD ["python", "/main.py"]
