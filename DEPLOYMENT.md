# Deployment - TimeInData

---
## Preparation

---
1. Checkout to `/deploy` branch
2. Copy `example.env` to `.env.production` and fill it with your data


## Deployment step-by-step guide

---
First, we need to configure our proxy, Traefik, to handle incoming connections and HTTPS certificates.
You need to do next steps:

### Configure docker-compose.traefik.yml
Create a remote directory to store your Traefik Docker Compose file by running the following command **on your server**:
```bash 
  mkdir -p /root/code/traefik-public/
```
Copy the Traefik Docker Compose file to your server. You could do it by running the command rsync **on your local machine**:
<br/><small>Don't forget to replace `your-server.example.com` with your actual server address.</small>
```bash
  rsync -a docker-compose.traefik.yml root@your-server.example.com:/root/code/traefik-public/
```

### Create a public network
Create a public network for Traefik to communicate with the other world.
Run the following command **on your server**:
```bash
  docker network create traefik-public
```

### Configure Traefik env variables
The `docker-compose.traefik.yml` file expects some environment variables to be set in your terminal before starting it. 
You can do it by running all the following commands in **your remote server**.
<br/><small>REMEMBER to change these credentials!</small>
1. Create the username for HTTP Basic Auth, e.g.:
    ```bash
    export USERNAME=admin
    ```
2. Create an environment variable with the password for HTTP Basic Auth, e.g.:
    ```bash
    export PASSWORD=changethis
    ```
3. Use openssl to generate the "hashed" version of the password for HTTP Basic Auth and store it in an environment variable:
    ```bash
    export HASHED_PASSWORD=$(openssl passwd -apr1 $PASSWORD)
    ```
4. To verify that the hashed password is correct, you can print it:
    ```bash
    echo $HASHED_PASSWORD
    ```
5. Create an environment variable with the domain name for your server, e.g.:
   ```bash
   export DOMAIN=time-in-data.example.com
   ```
6. Create an environment variable with the email for Let's Encrypt, e.g.:
   ```bash
   export EMAIL=admin@example.com
   ```

### Start the Traefik proxy
Now we configure all environment variables and ready to start the Traefik proxy **on your server**.

Go to the traefik directory:
```bash
  cd /root/code/traefik-public/
```
Run the following command to start the proxy:
```bash
  docker compose -f docker-compose.traefik.yml up -d
```

## Deploy services
After you have started the Traefik proxy, you can deploy services. You can do it by running the 
following command **on your local machine**:
1. Create Docker Context for running all commands on remote server:
   ```bash
   docker context create your-context --docker "host=ssh://root@your-server-ip"
   ```
2. Connect to your server via SSH:
   ```bash
   ssh root@your-server-ip
   ```
3. Up containers from `docker-compose.yml`:
   ```bash
   docker --context your-context compose --env-file .env.production -f docker-compose.yml up -d --build
   ```

---
### Sources
Use [The Fullstack FastAPI template](https://github.com/fastapi/full-stack-fastapi-template/blob/master/deployment.md) if 
you stuck with some part of the guide.
