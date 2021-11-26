FROM public.ecr.aws/lambda/python:3.9

RUN yum install xz atk cups-libs gtk3 libXcomposite alsa-lib tar \
    libXcursor libXdamage libXext libXi libXrandr libXScrnSaver \
    libXtst pango at-spi2-atk libXt xorg-x11-server-Xvfb \
    xorg-x11-xauth dbus-glib dbus-glib-devel unzip bzip2 -y -q

# # Install dependencies
# RUN yum install -y nodejs gcc-c++ make cups-libs dbus-glib libXrandr libXcursor libXinerama cairo cairo-gobject pango libXScrnSaver gtk3
# # On Amazon Linux 2 Downgrade ALSA library
# RUN yum remove -y alsa-lib-1.1.4.1-2.amzn2.i686 && yum install -y alsa-lib-1.1.3-3.amzn2.x86_64

# RUN mkdir -p "/opt/firefox" && \
#     curl -Lo "/tmp/firefox.tar.bz2" "http://ftp.mozilla.org/pub/firefox/releases/94.0b9/linux-x86_64/en-US/firefox-94.0b9.tar.bz2" && \
#     tar -jxf "/tmp/firefox.tar.bz2" -C "/opt/firefox/" && \
#     mv "/opt/firefox/firefox" "/opt/firefox/firefox-temp" && \
#     mv /opt/firefox/firefox-temp/* /opt/firefox/ && \
#     ln -s /opt/firefox/firefox /usr/bin/firefox && \
#     rm -rf "/tmp/firefox.tar.bz2"

RUN mkdir -p "/tmp/chrome" && \
    curl -Lo "/tmp/chrome/chrome-linux.zip" "https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Linux_x64%2F827102%2Fchrome-linux.zip?alt=media" && \
    unzip -q "/tmp/chrome/chrome-linux.zip" -d "/opt/chrome/" && \
    mv /opt/chrome/chrome-linux/* /opt/chrome/ && \
    ln -s /opt/chrome/chrome /usr/bin/google-chrome && \
    rm -rf /opt/chrome/chrome-linux && \
    rm -rf /tmp/chrome

RUN mkdir -p /opt/bin/ && \
    mkdir -p /opt/fonts/ && \
    mkdir -p /tmp/downloads/fonts && \
    curl -SL https://fonts.google.com/download?family=Noto%20Sans%20JP > /tmp/downloads/Noto_Sans_JP.zip && \
    #curl -SL https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm > /tmp/downloads/google-chrome.rpm && \
    #curl -SL https://dl.google.com/linux/chrome/rpm/stable/x86_64/google-chrome-beta-96.0.4664.18-1.x86_64.rpm > /tmp/downloads/google-chrome.rpm && \
    #curl -SL https://dl.google.com/linux/chrome/rpm/stable/x86_64/google-chrome-stable-85.0.4183.83-1.x86_64.rpm > /tmp/downloads/google-chrome.rpm && \
    # yum install -y amazon-linux-extras install epel && \
    # yum install -y /tmp/downloads/google-chrome.rpm && \
    unzip /tmp/downloads/Noto*.zip -d /tmp/downloads/fonts/ && \
    mv /tmp/downloads/fonts/NotoSansJP-Regular.otf /opt/fonts/ && \
    rm -rf /tmp/downloads

COPY server/requirements.txt ./
RUN pip install -r requirements.txt

COPY server/server.py ./
COPY server/helper.py ./
COPY server/picklelib.py ./
COPY server/fonts.conf /opt/fonts/
COPY server/versions/ ./versions/
COPY server/MultiPass-for-HTTP-basic-authentication.crx ./
CMD ["server.handler"]
