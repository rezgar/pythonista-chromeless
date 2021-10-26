FROM public.ecr.aws/lambda/python:3.9

RUN mkdir -p /opt/bin/ && \
    mkdir -p /opt/fonts/ && \
    mkdir -p /tmp/downloads/fonts && \
    curl -SL https://fonts.google.com/download?family=Noto%20Sans%20JP > /tmp/downloads/Noto_Sans_JP.zip && \
    curl -SL https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm > /tmp/downloads/google-chrome.rpm && \
    yum install -y /tmp/downloads/google-chrome.rpm && \
    yum install -y unzip && \
    unzip /tmp/downloads/Noto*.zip -d /tmp/downloads/fonts/ && \
    mv /tmp/downloads/fonts/NotoSansJP-Regular.otf /opt/fonts/ && \
    rm -rf /tmp/downloads

COPY sls/requirements.txt ./
RUN pip install -r requirements.txt

COPY sls/server.py ./
COPY sls/fonts.conf /opt/fonts/
COPY sls/versions/ ./versions/
CMD ["server.handler"]
