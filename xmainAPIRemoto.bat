f:
cd f:\python\afactura

uvicorn mainAPI:app --host 0.0.0.0 --port 3700 --reload --ssl-keyfile=./cer/30000000335718.key --ssl-certfile=./cer/tapetestufan.mx.pem