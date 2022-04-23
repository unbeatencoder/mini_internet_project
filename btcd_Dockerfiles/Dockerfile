# bitcoin-testnet-box docker image

FROM ubuntu 
LABEL maintainer="Sean Lavine <lavis88@gmail.com>"

ENV DEBIAN_FRONTEND noninteractive

# install dependencies
RUN apt-get update && \
	apt-get install --yes \
	make wget vim rsyslog locales iputils-ping traceroute \
  openssh-server tcpdump net-tools dnsutils iperf3 build-essential

# Set locale
RUN sed -i -e 's/# \(en_US\.UTF-8 .*\)/\1/' /etc/locale.gen && \
  locale-gen
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# Install bitcoin 
ENV BITCOIN_CORE_VERSION "0.21.0"

# download and install bitcoin binaries
RUN mkdir -p tmp \
	&& cd tmp \
	&& wget "https://bitcoincore.org/bin/bitcoin-core-${BITCOIN_CORE_VERSION}/bitcoin-${BITCOIN_CORE_VERSION}-x86_64-linux-gnu.tar.gz" \
	&& tar xzf "bitcoin-${BITCOIN_CORE_VERSION}-x86_64-linux-gnu.tar.gz" \
	&& cd "bitcoin-${BITCOIN_CORE_VERSION}/bin" \
	&& install --mode 755 --target-directory /usr/local/bin *

# clean up
RUN rm -r tmp

ENV HOME '/root'

# copy the testnet-box files into the image
# copy the config files into the bitcoin folder
RUN mkdir -p $HOME/.bitcoin
ADD bitcoin.conf $HOME/.bitcoin/

# Make directory for sshd on image
RUN mkdir -p $HOME/.ssh

# expose two rpc ports for the nodes to allow outside container access and one for ssh
EXPOSE 8333 8332 22


# set working dir to HOME so config files load correctly
WORKDIR $HOME

# Add startup script and set as default run
ADD startup.sh $HOME/startup.sh
RUN chmod +x $HOME/startup.sh
CMD ["./startup.sh"]
