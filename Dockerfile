FROM python:3.10.8

WORKDIR ./docker_demo
 
ADD . .

RUN pip install -r requirements.txt

CMD ["python", "./chat/Dingtalk.py"]
