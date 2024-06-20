#!/bin/bash
npm run buildit
chown -R $(whoami):www-data _site
