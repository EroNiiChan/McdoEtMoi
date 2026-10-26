FROM python:3.12-slim-bookworm

# 1. Installation de Chromium et son driver natif Debian
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    fonts-liberation \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# 2. Configuration du fuseau horaire Europe/Paris
ENV TZ=Europe/Paris
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /app

# 3. Installation des dépendances Python
RUN pip install --no-cache-dir selenium

# 4. Copie des fichiers du bot
COPY script.py Com.py ./

# Dossier pour les logs et screenshots et utilisateur non-root
RUN mkdir -p erreurs_screenshots && \
    useradd -u 1000 -m botuser && \
    chown -R botuser:botuser /app

USER botuser

CMD ["python", "-u", "script.py"]
