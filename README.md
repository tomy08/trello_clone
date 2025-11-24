# Trello Clone

Aplicación de gestión de tareas estilo Trello construida con Flask (backend) y React (frontend).

## Requisitos

- Docker
- Docker Compose

## Configuración

1. **Clonar el repositorio y navegar al directorio:**

   ```bash
   cd trello-clone
   ```

2. **Crear archivo .env en backend:**

   ```bash
   cp backend/.env.example backend/.env
   ```

3. **Construir y levantar los contenedores:**

   ```bash
   docker-compose up --build
   ```

4. **Acceder a la aplicación:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000
   - PostgreSQL: localhost:5432

## Comandos útiles

### Iniciar los servicios

```bash
docker-compose up
```

### Iniciar en segundo plano

```bash
docker-compose up -d
```

### Detener los servicios

```bash
docker-compose down
```

### Ver logs

```bash
docker-compose logs -f
```

### Reconstruir las imágenes

```bash
docker-compose up --build
```

### Ejecutar migraciones de base de datos

```bash
docker-compose exec backend flask db init
docker-compose exec backend flask db migrate -m "Initial migration"
docker-compose exec backend flask db upgrade
```

### Acceder a la base de datos

```bash
docker-compose exec db psql -U trello_user -d trello_db
```

### Detener y eliminar volúmenes

```bash
docker-compose down -v
```

## Desarrollo

Los volúmenes están configurados para reflejar cambios en tiempo real:

- Los cambios en el código del backend se reflejarán automáticamente
- Los cambios en el código del frontend activarán hot-reload

## Producción

Para producción, asegúrate de:

1. Cambiar las credenciales de la base de datos
2. Actualizar el `SECRET_KEY` en las variables de entorno
3. Configurar `FLASK_ENV=production`
4. Construir el frontend con `npm run build`
