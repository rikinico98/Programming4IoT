FROM python:3.7
COPY . .
RUN apt-get -y update && apt-get install -y libzbar-dev
RUN apt-get update && apt-get install -y python3-opencv
RUN pip3 install -r requirements.txt
RUN pip install opencv-python
CMD ["python3","./BOT_Beta_v2.py"]

