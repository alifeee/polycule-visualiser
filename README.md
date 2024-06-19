# Polycule Visualiser

A graph visualiser designed to be self-hosted.

![GIF of graph moving in a spring-like motion](./images/cule.gif)

## How to build site

### Install

```bash
npm install
cp polycule.json.example polycule.json
```

### Build site

```bash
npm run build
npm run dev
```

## Set up on server

```bash
git clone git@github.com:alifeee/polycule-visualiser /var/www/polycule
```

Add the following to nginx config (using `fastcgi`)

```nginx
location /polycule/ {
        alias /var/www/polycule/_site/;
        try_files $uri $uri/ =404;
}
location /polycule/edit {
        fastcgi_intercept_errors on;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME /var/www/polycule/edit.cgi;
        fastcgi_pass unix:/var/run/fcgiwrap.socket;
}
```
