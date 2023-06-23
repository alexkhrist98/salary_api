FROM python:3.11
WORKDIR /root
COPY main.py /root
COPY app /root/app
COPY requirements.txt /root
COPY .env /root
RUN pip install virtualenv
RUN virtualenv venv
RUN chmod +x venv/bin/activate
ENV PATH="/salary_api/venv/bin:$PATH"
RUN pip install -r requirements.txt
EXPOSE 8000
CMD venv/bin/activate && python main.py