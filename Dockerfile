FROM python:slim
ENV PYTHONUNBUFFERED=1
WORKDIR /opt/qbf_support_bot
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY bot ./bot
CMD ["python", "-m", "bot"]
