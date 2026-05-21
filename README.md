# Wallet segura de metodos de pago

Aplicacion full-stack que permite a una persona crear una cuenta, iniciar
sesion y administrar sus metodos de pago (tarjetas, cuentas bancarias y CLABE)
de forma segura. Los identificadores se cifran antes de tocar la base y cada
operacion relevante deja huella en una bitacora de auditoria.

El proyecto se entrega como solucion a una prueba tecnica. La interfaz toma
como referencia el lenguaje visual de [taveron.com](https://taveron.com),
combinado con un comportamiento tipo Apple Wallet para mostrar las tarjetas
apiladas en el listado.

---

## Stack

- **Backend**: Python 3.12 con FastAPI, SQLAlchemy 2 y Alembic.
- **Base de datos**: PostgreSQL 16.
- **Frontend**: React 18 con Vite, React Router y Tailwind CSS.
- **Autenticacion**: JWT (HS256) emitidos desde el backend.
- **Cifrado de datos sensibles**: Fernet (AES-128-CBC + HMAC-SHA256) de la
  libreria `cryptography`.
- **Contenedores**: Docker y Docker Compose para levantar todo el stack con
  un solo comando.

---

## Estructura del repositorio

```
.
|-- backend/                    API FastAPI organizada por capas
|   |-- app/
|   |   |-- core/               configuracion, BD, seguridad, cifrado
|   |   |-- models/             modelos SQLAlchemy
|   |   |-- schemas/            esquemas Pydantic
|   |   |-- services/           logica de negocio (auth, payment, audit)
|   |   |-- controllers/        endpoints REST agrupados por modulo
|   |   `-- main.py             punto de entrada
|   |-- alembic/                migraciones de base de datos
|   |-- tests/                  pruebas con pytest
|   |-- requirements.txt
|   |-- Dockerfile
|   `-- .env.example
|-- frontend/                   SPA en React + Vite + Tailwind
|   |-- src/
|   |   |-- pages/              vistas principales
|   |   |-- components/         piezas reutilizables (Navbar, WalletStack, etc.)
|   |   |-- context/            AuthContext con persistencia en localStorage
|   |   `-- services/api.js     cliente axios con interceptores
|   |-- Dockerfile
|   `-- .env.example
|-- docs/
|   |-- ARCHITECTURE.md         diagrama y explicacion de arquitectura
|   |-- DATABASE.md             diagrama ER y decisiones del modelo de datos
|   `-- SECURITY.md             manejo de datos sensibles y trazabilidad
|-- docker-compose.yml          stack completo (db + backend + frontend)
`-- .env.example                variables compartidas por los servicios
```

---

## Despliegue paso a paso en una maquina nueva

Esta seccion asume que estas clonando el repo en una maquina que no ha
ejecutado el proyecto antes. Si solo quieres correrlo, basta con seguir los
pasos en orden.

### 1. Requisitos previos

Necesitas instalado lo siguiente:

- **Docker** version 24 o superior.
- **Docker Compose** v2 (viene incluido con Docker Desktop, y en Linux se
  instala con `apt install docker-compose-plugin`).
- **Git** para clonar el repo.

Para verificar que todo este en orden:

```bash
docker --version
docker compose version
git --version
```

> Si vas a correrlo sin Docker (modo manual) tambien necesitas Python 3.12,
> Node 20 y una instancia local de PostgreSQL 16. Mas abajo dejo la guia para
> ese flujo, pero recomiendo Docker porque ahorra dolores de cabeza.

### 2. Clonar el repositorio

```bash
git clone https://github.com/RicardoZavala12/taveron_pruebaRICARDOZAVALA.git
cd taveron_pruebaRICARDOZAVALA
```

### 3. Crear el archivo .env

El stack lee sus variables sensibles desde un `.env` en la raiz. Hay una
plantilla lista (`.env.example`) que se puede copiar tal cual:

```bash
cp .env.example .env
```

Hay tres variables que **si o si** se tienen que cambiar antes de levantar
el stack:

- `FERNET_KEY`: la llave de cifrado de los identificadores. Tiene que ser una
  llave Fernet valida (base64 url-safe de 32 bytes).
- `JWT_SECRET_KEY`: cualquier cadena larga y aleatoria.
- `FINGERPRINT_PEPPER`: cualquier cadena, debe mantenerse estable por
  instalacion.

Para generar una `FERNET_KEY` se puede usar este one-liner con Docker (no
necesita Python instalado):

```bash
docker run --rm python:3.12-slim sh -c "pip install -q cryptography && python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
```

Copia el valor que imprime y pegalo como `FERNET_KEY=...` dentro del `.env`.

Si tu maquina ya tiene PostgreSQL corriendo en el puerto 5432, cambia
`POSTGRES_PORT` a uno libre (por ejemplo `5435`). Eso solo afecta el puerto
que se publica al host; el backend dentro de la red de Docker sigue
hablandole al contenedor `db` en 5432.

### 4. Levantar el stack

```bash
docker compose up --build
```

Este comando hace tres cosas:

1. Levanta PostgreSQL 16 con el volumen `wallet_db_data` para persistencia.
2. Construye la imagen del backend, espera a que la base este saludable,
   corre `alembic upgrade head` para aplicar las migraciones y arranca
   Uvicorn en `http://localhost:8000` con recarga en caliente.
3. Construye el frontend con Node 20 y levanta Vite en
   `http://localhost:5173`.

La primera vez tarda unos 3-4 minutos por la descarga de imagenes y el
`npm install`. Cuando todo este arriba se ve algo como:

```
wallet_db        | database system is ready to accept connections
wallet_backend   | INFO:     Application startup complete.
wallet_frontend  | VITE v5.4.21  ready in 323 ms
```

### 5. Abrir la aplicacion

- Frontend: <http://localhost:5173>
- API: <http://localhost:8000>
- Documentacion interactiva (Swagger): <http://localhost:8000/docs>

### 6. Correr las pruebas

Con el stack arriba se pueden correr las pruebas dentro del contenedor:

```bash
docker exec wallet_backend pytest -q
```

Se espera ver `30 passed`. No hace falta una base externa: las pruebas usan
SQLite en memoria.

### 7. Apagar el stack

```bash
docker compose down
```

Si quieres tambien borrar la base de datos (perdiendo todos los registros):

```bash
docker compose down -v
```

---

## Como usar la aplicacion

### Crear una cuenta

1. Abre <http://localhost:5173>.
2. Click en "Registrate".
3. Llena nombre, correo y una contrasena de minimo 8 caracteres, con al
   menos una letra y un numero.
4. Al confirmar, el frontend te loguea automaticamente y te lleva al
   listado de metodos de pago (que arranca vacio).

### Registrar un metodo de pago

Desde el listado, click en "Agregar metodo". El formulario pide:

- **Tipo**: tarjeta, cuenta bancaria, CLABE u otro.
- **Moneda**: MXN, USD o EUR.
- **Alias**: como quieres llamarle (ej. "Debito personal").
- **Institucion**: lista desplegable con los principales bancos y fintechs
  de Mexico. Si tu institucion no aparece, selecciona "Otra" y escribe el
  nombre.
- **Numero de tarjeta / identificador**: cualquier secuencia alfanumerica
  de 4 a 40 caracteres. No se valida algoritmo Luhn, asi que puedes usar
  cualquier numero.

#### Numeros de prueba sugeridos por marca

Si quieres llenar el listado con tarjetas que se vean reales y que mantienen
el patron de cada marca (BIN inicial), puedes usar estos:

| Marca       | Numero para copiar y pegar | Mostrado en pantalla   |
|-------------|----------------------------|------------------------|
| Visa        | `4111111111111111`         | `4111 1111 1111 1111`  |
| Visa        | `4242424242424242`         | `4242 4242 4242 4242`  |
| Mastercard  | `5500000000000004`         | `5500 0000 0000 0004`  |
| Mastercard  | `5555555555554444`         | `5555 5555 5555 4444`  |
| Amex        | `378282246310005`          | `3782 822463 10005`    |

Ninguno de estos numeros es real, son patrones publicos que se usan en
sandboxes de pasarelas de pago (Stripe, PayPal, Mercado Pago) para validar
formato. La aplicacion no procesa pagos, asi que tampoco importa: cualquier
numero alfanumerico de 4 a 40 caracteres sirve.

#### Regla de no duplicados

El backend calcula un fingerprint HMAC-SHA256 del identificador y no
permite registrar dos veces el mismo numero por usuario. Si lo intentas,
veras el mensaje "Ya tienes registrado este metodo de pago".

### Ver el detalle, desactivar o eliminar

- En el listado las tarjetas se muestran apiladas tipo Apple Wallet. Al
  pasar el mouse sobre una se eleva y las de abajo se desplazan. Click
  sobre la card seleccionada abre el detalle.
- Desde el detalle se puede **desactivar** (queda visible pero marcada como
  inactiva) o **eliminar** (soft delete: deja de aparecer pero el renglon
  se conserva con `is_deleted = true` para preservar la trazabilidad).

### Cambiar la contrasena

En la pantalla de perfil hay una card "Cambiar contrasena" donde se puede
actualizar la contrasena ingresando la actual y la nueva.

### Filtros y vista completa

Cuando hay mas de 6 metodos, el stack solo muestra los primeros y aparece
un boton "Ver todos" que cambia a una grilla paginada con filtros por tipo
y por estatus.

---

## Variables de entorno

| Variable             | Descripcion                                                          |
|----------------------|----------------------------------------------------------------------|
| `POSTGRES_USER`      | Usuario de PostgreSQL.                                               |
| `POSTGRES_PASSWORD`  | Contrasena del usuario.                                              |
| `POSTGRES_DB`        | Nombre de la base.                                                   |
| `POSTGRES_PORT`      | Puerto que publica Postgres al host (5432 por defecto).              |
| `DATABASE_URL`       | URL completa de conexion (la arma docker-compose).                   |
| `APP_ENV`            | `development`, `testing` o `production`.                             |
| `JWT_SECRET_KEY`     | Secreto para firmar los JWT.                                         |
| `JWT_ALGORITHM`      | Algoritmo de firma (HS256 por defecto).                              |
| `JWT_EXPIRE_MINUTES` | Minutos de vigencia del token.                                       |
| `FERNET_KEY`         | Llave Fernet (base64 url-safe) para cifrar los identificadores.      |
| `FINGERPRINT_PEPPER` | Pimienta usada en el HMAC del fingerprint de duplicados.             |
| `CORS_ORIGINS`       | Origenes permitidos para CORS, separados por coma.                   |
| `VITE_API_URL`       | URL del backend que consume el frontend.                             |

---

## Endpoints principales

| Metodo  | Ruta                                | Descripcion                                           |
|---------|-------------------------------------|-------------------------------------------------------|
| POST    | `/auth/register`                    | Crea un usuario nuevo.                                |
| POST    | `/auth/login`                       | Devuelve un JWT y los datos del usuario.              |
| POST    | `/auth/logout`                      | Registra el cierre de sesion en la bitacora.          |
| GET     | `/users/me`                         | Perfil del usuario autenticado.                       |
| PUT     | `/users/me/password`                | Cambia la contrasena (requiere la actual).            |
| GET     | `/payment-methods`                  | Lista paginada y filtrable (`status`, `type`, `page`, `size`). |
| POST    | `/payment-methods`                  | Alta de un metodo de pago.                            |
| GET     | `/payment-methods/{id}`             | Detalle de un metodo del usuario.                     |
| PATCH   | `/payment-methods/{id}/deactivate`  | Desactiva (sin borrar) el metodo.                     |
| DELETE  | `/payment-methods/{id}`             | Soft delete.                                          |

La documentacion interactiva con ejemplos de cada endpoint vive en
`/docs` (Swagger UI) y `/redoc`.

---

## Levantar el proyecto sin Docker

Si por algun motivo no se puede usar Docker, los pasos son:

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Editar .env y poner DATABASE_URL apuntando a tu Postgres local
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

---

## Decisiones de diseno

Las decisiones que considere relevantes estan documentadas con mas detalle
en la carpeta `docs/`:

- [Arquitectura](docs/ARCHITECTURE.md): capas, flujo de una operacion,
  responsabilidades de cada modulo.
- [Base de datos](docs/DATABASE.md): diagrama ER, indices, constraint de
  unicidad por usuario, soft delete.
- [Seguridad y trazabilidad](docs/SECURITY.md): manejo del identificador
  con Fernet, fingerprint HMAC, bcrypt para contrasenas, contenido de la
  tabla de auditoria.

Resumen rapido de las decisiones que mas peso tuvieron:

- **Tres columnas para el identificador**: `identifier_encrypted` (cifrado
  Fernet), `identifier_last4` (visible) y `identifier_fingerprint` (HMAC
  para deteccion de duplicados sin descifrar).
- **Soft delete** en `payment_methods` para preservar la auditoria.
- **Auditoria centralizada** en `audit_service.record_event` con un enum
  tipado de acciones.
- **Servicios delgados** con excepciones de negocio propias (`AuthError`,
  `PaymentMethodError`) que los controladores traducen a `HTTPException`.

---

## Pruebas

Suite con pytest, 30 casos en total cubriendo:

- Registro, login, perfil, cambio de contrasena, intentos fallidos.
- Alta de metodos de pago con diferentes tipos.
- Deteccion de duplicados.
- Paginacion y filtros.
- Desactivacion y soft delete.
- Aislamiento entre usuarios (un usuario no ve metodos de otro).
- Roundtrip de cifrado y consistencia del fingerprint.

Para correrlas:

```bash
# Con el stack levantado
docker exec wallet_backend pytest -q

# Localmente (sin Docker)
cd backend
pytest -q
```

---

## Problemas comunes

**El puerto 5432 ya esta ocupado.**
Probablemente tienes otra instancia de Postgres corriendo. Cambia
`POSTGRES_PORT` en el `.env` a un puerto libre (por ejemplo 5435).

**El frontend no se conecta al backend.**
Revisa que `VITE_API_URL` en el `.env` apunte a `http://localhost:8000`. Si
levantaste el backend en otro puerto, ajusta tambien `CORS_ORIGINS`.

**Olvide la contrasena.**
La prueba no exige flujo de "olvide mi contrasena" por correo. Lo que si
existe es el cambio de contrasena estando logueado, desde la pantalla de
perfil. Si perdiste el acceso por completo, lo mas rapido es resetear la
base con `docker compose down -v` y volver a registrarse.

**Quiero ver el contenido de la base.**
Con el stack levantado:

```bash
docker exec -it wallet_db psql -U wallet_user -d wallet
```

Algunas consultas utiles:

```sql
SELECT id, email, full_name, created_at FROM users;
SELECT id, alias, type, identifier_last4, status FROM payment_methods;
SELECT action::text, ip_address, created_at FROM audit_logs ORDER BY id DESC LIMIT 20;
```

---

## Ricardo Daniel FLores Zavala

Uso para fines de entrevista tecnica para TAVERON como Desarrollador Full Stack.
