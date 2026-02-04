# Use a slim Debian image as the base
FROM debian:bookworm-slim

# Install sudo and create a non-root user
RUN apt-get update && apt-get install -y sudo && rm -rf /var/lib/apt/lists/*
RUN useradd -m -s /bin/bash jules
RUN adduser jules sudo
RUN echo "jules:jules" | chpasswd

# Switch to the non-root user
USER jules
WORKDIR /home/jules

# Install dependencies
RUN sudo apt-get update && \
    sudo apt-get install -y \
    curl \
    openssl \
    git \
    msmtp \
    ca-certificates \
    libnss3 \
    davfs2 \
    && sudo rm -rf /var/lib/apt/lists/*

# Install Node.js and Firebase Tools
RUN curl -sL https://deb.nodesource.com/setup_22.x | sudo -E bash - && \
    sudo apt-get install -y nodejs && \
    sudo npm install -g firebase-tools

# Install GitHub CLI (gh)
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg && \
    sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null && \
    sudo apt-get update && \
    sudo apt-get install -y gh

# Install Google Cloud CLI
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    sudo apt-get update && \
    sudo apt-get install -y google-cloud-cli

# Copy the jules.sh script into the container
COPY --chown=jules:jules jules.sh .
RUN sudo chmod +x jules.sh

# Set the entrypoint
ENTRYPOINT ["./jules.sh"]