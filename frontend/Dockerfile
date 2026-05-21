# Imagen oficial de Node 20 sobre Alpine para mantener el tamano bajo.
FROM node:20-alpine

WORKDIR /app

# Se copian primero los manifiestos para aprovechar la cache de Docker:
# mientras no cambien package.json / package-lock.json no se reinstala todo.
COPY package.json package-lock.json* ./
RUN npm install

# Se copia el resto del codigo (durante desarrollo se monta como volumen,
# pero la imagen base ya queda completa por si se corre standalone).
COPY . .

EXPOSE 5173

# Vite en modo desarrollo escuchando en todas las interfaces para que sea
# accesible desde el host al correr con docker-compose.
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
