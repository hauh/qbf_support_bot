FROM python:slim
WORKDIR /opt/qbf_support_bot
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY bot ./bot
COPY menu.xlsx .
CMD ["python", "-m", "bot"]
