FROM srt749/salt_scrape-transform

# font libraries required to run on headless chrome

RUN apt-get update && \
    apt-get -qq -y install  libxpm4 libxrender1 libgtk2.0-0 libnss3\ 
    libgconf-2-4  libpango1.0-0 libxss1 libxtst6 fonts-liberation\ 
    libappindicator1 xdg-utils

RUN apt-get -y install \
    xvfb gtk2-engines-pixbuf \
    xfonts-cyrillic xfonts-100dpi xfonts-75dpi xfonts-base xfonts-scalable \
    imagemagick x11-apps zip

# download and install chrome version 86

RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm \
	rpm -i google-chrome-stable_current_x86_64.rpm

