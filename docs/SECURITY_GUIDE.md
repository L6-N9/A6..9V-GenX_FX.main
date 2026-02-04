# Security Guide for `jules.sh`

Several commands in the `jules.sh` script are commented out by default. This is a safety measure to prevent unintentional actions that could modify your server, deploy to cloud services, or expose sensitive credentials.

This guide explains the purpose of these commands and how to enable them securely.

## 1. `reverse_proxy`

This command generates an Apache configuration and is intended to be copied to a remote server. The `scp` and `ssh` commands are commented out to prevent accidental server modifications.

### To enable:

1.  **Set up passwordless SSH:** For the `scp` and `ssh` commands to work without manual password entry, you need to set up SSH key-based authentication.
    -   Generate an SSH key pair on the machine where you are running the script (or inside the Docker container).
    -   Copy the public key to the `~/.ssh/authorized_keys` file on your remote server (`user@server354.web-hosting.com`).

2.  **Uncomment the commands:** In `jules.sh`, find the `reverse_proxy` function and uncomment the `scp` and `ssh` lines.

    ```bash
    # reverse_proxy() {
    ...
      scp remote.conf user@server354.web-hosting.com:/etc/apache2/sites-available/
      ssh user@server354.web-hosting.com "a2ensite remote && systemctl reload apache2"
    # }
    ```

## 2. `firebase_session`

This command deploys Firestore security rules to your Firebase project. It requires you to be authenticated with Firebase.

### To enable:

1.  **Log in to Firebase:** Before running the script, you need to log in to your Firebase account. You can do this interactively inside the container:
    ```bash
    docker run --rm -it jules-orchestrator /bin/bash
    firebase login
    ```
    This will provide a URL to authenticate in your browser.

2.  **Uncomment the command:** In `jules.sh`, uncomment the `firebase deploy` line in the `firebase_session` function.

## 3. `note_sync`

This command mounts a WebDAV share using `davfs2`. It requires credentials to authenticate with the WebDAV server.

### To enable:

1.  **Configure `davfs2` secrets:** The `davfs2` tool uses a secrets file to store credentials. You will need to provide the username and password for your WebDAV share.
    -   Inside the container (in interactive mode), you can create or edit the `/home/jules/.davfs2/secrets` file (or `/etc/davfs2/secrets` for system-wide configuration). Add a line like this:
        ```
        http://remote.genxfx.org your_username your_password
        ```
    -   **Security Note:** For better security, you can mount a local secrets file into the container at runtime using Docker volumes.

2.  **Uncomment the mount command:** In `jules.sh`, uncomment the `mount` command in the `note_sync` function.

## 4. `send_alert`

This command sends an email using `msmtp`. It requires you to configure `msmtp` with your email provider's SMTP settings and your credentials.

### To enable:

1.  **Configure `msmtp`:** You need to create a configuration file for `msmtp`. A good location is `~/.msmtprc` inside the container.
    -   An example configuration for Gmail might look like this:
        ```
        defaults
        auth           on
        tls            on
        tls_trust_file /etc/ssl/certs/ca-certificates.crt
        logfile        ~/.msmtp.log

        account        gmail
        host           smtp.gmail.com
        port           587
        from           your_email@gmail.com
        user           your_email@gmail.com
        password       your_app_password

        account default : gmail
        ```
    -   **Security Note:** It is highly recommended to use an "App Password" if your email provider supports it, rather than your main account password. You can mount a local `.msmtprc` file into the container for better security.

2.  **Uncomment the `msmtp` command:** In `jules.sh`, uncomment the `msmtp` command in the `send_alert` function.