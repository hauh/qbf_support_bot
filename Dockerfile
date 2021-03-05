FROM python:slim
ENV PYTHONUNBUFFERED=1 \
	PYTHONDONTWRITEBYTECODE=1
WORKDIR /opt/qbf_support_bot
COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
	pip install --no-cache-dir -r requirements.txt
COPY bot ./bot
CMD ["python", "-m", "bot"]
