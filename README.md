# Polycule Visualiser

A graph visualiser designed to be self-hosted, using [Springy]

See a non-editable example → <http://alifeee.co.uk/polycule-visualiser/>

![GIF of graph moving in a spring-like motion](./images/cule.gif)

The graph is defined by YAML:

```yaml
nodes:
  - name: Seraphina
  - name: Elfo
  - name: France
edges:
  - from: Seraphina
    to: Elfo
  - from: Elfo
    to: France
    type: dashed
```

## How to use locally

1. Download the files ([as a zip](https://github.com/alifeee/polycule-visualiser/archive/refs/heads/main.zip)) and extract to a folder
1. open `index.html` with a text editor (Notepad/etc)
1. edit the polycule at the top of the file
1. open (double click or open in browser) `index.html`

## How to install on a server with editing

```bash
mkdir -p /var/www/
git clone git@github.com:alifeee/polycule-visualiser /var/www/polycule
cd /var/www/polycule

cp .env.example .env
cp polycule.yaml.example polycule.yaml
# We change the ownership of the built files, so that the www-data user can change them later.
sudo chown $USER:www-data polycule.yaml

# Generate a password file for the site
sudo htpasswd -c /etc/nginx/polycule.htpasswd <new_user>
```

Add the following to nginx config (using `fastcgi`)

```nginx
location /polycule/ {
    alias /usr/alifeee/polycule/;
    try_files $uri $uri/ =404;

    auth_basic_user_file /etc/nginx/polycule.htpasswd;
    auth_basic "polycule";
}
location ~ ^(/polycule/edit|/polycule/rss) {
    fastcgi_intercept_errors on;
    include fastcgi_params;
    fastcgi_param SCRIPT_FILENAME /usr/alifeee$fastcgi_script_name;
    fastcgi_pass unix:/var/run/fcgiwrap.socket;

    auth_basic_user_file /var/www/polycule/.htpasswd;
    auth_basic "polycule";
}
```

[Springy]: http://getspringy.com/
