FROM python:3

RUN apt-get update
RUN apt-get install -y yasm libmp3lame-dev

RUN mkdir -p /tmp/ffmpeg
RUN cd /tmp/ffmpeg
RUN wget https://www.ffmpeg.org/releases/ffmpeg-4.2.tar.gz
RUN tar -xzf ffmpeg-4.2.tar.gz; rm -r ffmpeg-4.2.tar.gz
RUN cd ./ffmpeg-4.2; ./configure --enable-gpl --enable-libmp3lame --enable-decoder=mjpeg,png --enable-encoder=png --enable-openssl --enable-nonfree
RUN cd ./ffmpeg-4.2; make
RUN cd ./ffmpeg-4.2; make install

RUN mkdir -p /app
RUN mkdir -p /app/workspace
RUN mkdir -p /app/workspace-output
WORKDIR /app/

RUN cd /app
COPY . /app/

RUN pip install -r requirements.txt

CMD [ "python", "-m", "transcoder_pipeline" ]
