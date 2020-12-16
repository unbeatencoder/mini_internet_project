FROM thomahol/d_p4

# Install ExaBGP
RUN apt-get update && apt-get install -y unzip python2.7 python3-dev

WORKDIR /root
RUN curl -O -L https://github.com/Exa-Networks/exabgp/archive/4.2.7.zip
RUN unzip 4.2.7.zip

RUN mkdir /etc/exabgp

RUN mkdir -p /exabgp-4.2.7/etc/exabgp
ENV PATH /root/exabgp-4.2.7/bin:/root/exabgp-4.2.7/sbin:$PATH

RUN exabgp --fi > /root/exabgp-4.2.7/etc/exabgp/exabgp.env

#COPY nanomsg_client.py /home/nanomsg_client.py
COPY docker-start /usr/sbin/docker-start
RUN chmod +x /usr/sbin/docker-start
ENTRYPOINT ["/usr/sbin/docker-start"]
