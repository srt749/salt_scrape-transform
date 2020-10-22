FROM srt749/salt_scrape-transform

RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm

RUN rpm -i google-chrome-stable_current_x86_64.rpm

RUN python.exe .\main.py