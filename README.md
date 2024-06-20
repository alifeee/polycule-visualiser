# Polycule Visualiser

A graph visualiser designed to be self-hosted.

See a non-editable example -> <http://alifeee.co.uk/polycule-visualiser/>

![GIF of graph moving in a spring-like motion](./images/cule.gif)

## How to build site

### Install

Install dependencies & copy site-specific data files.

```bash
npm install
cp polycule.json.example polycule.json
nano polycule.json
cp _data/URIs.json.example _data/URIs.json
nano _data/URIs.json
```

### Build site

We build with a script, which changes the ownership of the built files, so that the www-data user can change them later.

```bash
./build.sh
```

### Develop

```bash
npm run dev
```

## Set up on server

```bash
mkdir -p /var/www/
git clone git@github.com:alifeee/polycule-visualiser /var/www/polycule
```

Generate a password file for the site

```bash
sudo htpasswd -c /var/www/polycule/.htpasswd <new_user>
```

Add the following to nginx config (using `fastcgi`)

```nginx
location /polycule/ {
        alias /var/www/polycule/_site/;
        try_files $uri $uri/ =404;
        auth_basic "polycule";
        auth_basic_user_file /var/www/polycule/.htpasswd;
}
location /polycule/edit {
        fastcgi_intercept_errors on;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME /var/www/polycule/edit.cgi;
        fastcgi_pass unix:/var/run/fcgiwrap.socket;
        auth_basic "polycule";
        auth_basic_user_file /var/www/polycule/.htpasswd;
}
```
