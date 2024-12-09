# FROM python:3.12.7
#
# WORKDIR /app
#
# COPY requirements.txt requirements.txt
# RUN pip install -r requirements.txt
# COPY . .
#
# COPY entrypoint.sh /entrypoint.sh
# RUN chmod +x /entrypoint.sh
#
# ENTRYPOINT ["/entrypoint.sh"]


FROM python:3.12.7

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ /app/app/
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
