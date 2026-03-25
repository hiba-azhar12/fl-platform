# FL Finance Platform — Step 3

## Structure du projet

```
fl-finance-platform/
├── docker-compose.yml
├── README.md
├── server/
│   ├── server.py
│   └── Dockerfile
├── client/
│   ├── client.py
│   └── Dockerfile
├── certs/
│   └── generate_certs.sh
└── data/
    ├── train_A.parquet   (Node A)
    ├── test_A.parquet
    ├── train_B.parquet   (Node B)
    ├── test_B.parquet
    ├── train_C.parquet   (Node C — IEEE-CIS)
    ├── test_C.parquet
    ├── train_D.parquet   (Node D)
    └── test_D.parquet
```

## Etapes avant le lancement

### 1. Generer les certificats mTLS

```bash
cd certs/
bash generate_certs.sh
```

### 2. Placer les fichiers parquet dans data/

Copier les 8 fichiers parquet (train + test pour chaque noeud) dans le dossier data/.

### 3. Lancer le cluster FL

```bash
docker compose up --build
```

## Ce que vous devez voir dans les logs

```
fl-server  | Flower server running (10 rounds)
bank-a     | [bank_a] Modele initialise
bank-c     | [bank_c] Modele initialise
bank-b     | [bank_b] Modele initialise
bank-d     | [bank_d] Modele initialise
bank-a     | [bank_a] Round termine — DP applique (sigma=0.1)
bank-a     | [bank_a] F1-Score : 0.XXXX
fl-server  | Round 1 — F1 agrege : 0.XXXX
```

## Demo pour le meeting — rejeter un noeud non autorise

Ajouter un 5eme service sans certificat valide dans docker-compose.yml :

```yaml
  intrus:
    build: ./client
    environment:
      - BANK_ID=intrus
      - TRAIN_PATH=/data/train_A.parquet
      - TEST_PATH=/data/test_A.parquet
      - SERVER_ADDRESS=fl-server:8080
    volumes:
      - ./data:/data
    networks:
      - fl-network
```

Sans le volume ./certs:/certs, le client ne peut pas lire ca.crt
et la connexion mTLS est refusee automatiquement.
