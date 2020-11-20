FROM python:3.9
WORKDIR /opt/qbf_support_bot
COPY requirements.txt menu.xlsx ./
RUN apt-get update && apt-get upgrade -y && \
	pip install -r requirements.txt
EXPOSE 7002
COPY bot ./bot
CMD ["python", "-m", "bot"]
