#!/bin/bash

sudo systemctl restart atomicdex-api.service
echo "Use 'tail -f ~/logs/atomicdex-api.log' to view the logs"