From python:3.8

RUN pip install --upgrade pip
RUN pip install lxml==4.7.1
RUN pip install requests==2.27.1

RUN git clone https://github.com/milk4candy/website_traffic_simulator.git /opt/website_traffic_simulator/
WORKDIR /opt/website_traffic_simulator
ENTRYPOINT ["python", "./send_requests.py"]
CMD []
