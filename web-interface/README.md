# ZTS Data Lake Web Interface

A simple, production-ready web interface for the Zero Trust Security IoT Data Lake system.

## Features

- **Dashboard**: Real-time trust analytics and system overview
- **Data Explorer**: Browse and filter sensor data by profile
- **Traceability Viewer**: Complete audit trail of all data access
- **Schema Browser**: View and explore data schemas

## Architecture

This is a **single-file HTML/JavaScript application** with:
- No build process required
- No npm dependencies at runtime
- Pure vanilla JavaScript
- Nginx for serving and API proxying
- Zero Trust Security theme with dark mode

## Quick Start

### Using Docker Compose (Recommended)

The web interface is already configured in the main `docker-compose.yml`:

```bash
# From the project root directory
docker-compose up -d web_interface
```

Access the interface at: **http://localhost:3000**

### Manual Deployment

1. **Build the Docker image**:
```bash
cd web-interface
docker build -t zts-web-interface .
```

2. **Run the container**:
```bash
docker run -d -p 3000:80 --name zts-web zts-web-interface
```

3. **Access**: Open http://localhost:3000 in your browser

## File Structure

```
web-interface/
├── public/
│   └── index.html          # Single-file web application
├── Dockerfile              # Nginx-based container
└── README.md              # This file
```

## API Integration

The web interface communicates with the Consumer Gateway API through nginx proxy:

- **Frontend**: `http://localhost:3000`
- **API Proxy**: `http://localhost:3000/api/*` → `http://consumer-gateway:5000/*`

### API Endpoints Used

- `GET /profiles` - List all data profiles
- `GET /data/profile/{profile_id}` - Get data for a profile
- `GET /access-logs` - View access logs
- `GET /schemas` - List all schemas

## Configuration

### Change API Port

Edit the `docker-compose.yml` to change the web interface port:

```yaml
web_interface:
  ports:
    - "8080:80"  # Change 3000 to your preferred port
```

### Customize Nginx

The Dockerfile creates the nginx configuration. To customize:

1. Create `nginx.conf` file
2. Update Dockerfile to copy it:
```dockerfile
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

## Development

### Local Development (without Docker)

1. **Start a local web server**:
```bash
cd public
python3 -m http.server 8000
```

2. **Update API endpoint** in `index.html`:
```javascript
const API_BASE = 'http://localhost:5000';  // Direct to Consumer Gateway
```

3. **Access**: http://localhost:8000

### Customization

The entire application is in `public/index.html`. You can customize:

- **Colors**: Modify CSS variables in the `<style>` section
- **Features**: Add new functions in the `<script>` section
- **Layout**: Update HTML structure in the `<body>` section

## Security Features

- **Zero Trust Theme**: Visual indicators for trusted/untrusted data
- **Trust Score Display**: Color-coded trust percentages
- **Access Logging**: Complete audit trail visibility
- **Data Verification**: Shows signed/unsigned status

## Browser Compatibility

Works with all modern browsers:
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## Troubleshooting

### Web interface not loading

1. Check if container is running:
```bash
docker ps | grep web_interface
```

2. Check logs:
```bash
docker logs iot_web_interface
```

### API errors

1. Verify Consumer Gateway is running:
```bash
docker ps | grep consumer_gateway
```

2. Test API directly:
```bash
curl http://localhost:5000/profiles
```

### Port conflicts

If port 3000 is in use, change it in `docker-compose.yml`:
```yaml
ports:
  - "8080:80"  # Use different port
```

## Performance

- **Load Time**: < 1 second
- **Bundle Size**: ~15KB (single HTML file)
- **API Response**: Depends on data volume
- **Memory Usage**: ~50MB (nginx container)

## Future Enhancements

Potential additions (would require build process):
- Real-time data updates via WebSocket
- Advanced data visualization charts
- Export functionality (CSV, JSON)
- User authentication
- Dark/light theme toggle

## License

Part of the ZTS Data Lake project.