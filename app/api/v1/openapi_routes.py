"""Routes for serving OpenAPI JSON specification and Swagger UI."""

import logging
from flask import jsonify, current_app
from app.api.v1 import api_v1_bp

logger = logging.getLogger(__name__)


@api_v1_bp.route('/openapi.json', methods=['GET'])
def get_openapi_spec():
    """Serve OpenAPI JSON specification.
    
    Returns:
        JSON response with complete OpenAPI 3.0 specification
    """
    logger.info("OpenAPI JSON specification requested")
    
    try:
        # Get OpenAPI generator from app context
        openapi_generator = current_app.openapi_generator
        
        # Generate and return specification
        spec = openapi_generator.generate_spec()
        
        logger.debug("Successfully generated OpenAPI specification")
        return jsonify(spec)
        
    except Exception as e:
        logger.error(f"Error generating OpenAPI specification: {e}")
        return jsonify({
            'error': 'Failed to generate OpenAPI specification',
            'details': str(e)
        }), 500


@api_v1_bp.route('/docs', methods=['GET'])
def get_swagger_ui():
    """Serve Swagger UI interface for API documentation.
    
    Returns:
        HTML response with embedded Swagger UI
    """
    logger.info("Swagger UI documentation requested")
    
    # Embedded Swagger UI HTML template
    swagger_ui_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DHCP Network Management API - Documentation</title>
        <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css" />
        <style>
            html { box-sizing: border-box; overflow: -moz-scrollbars-vertical; overflow-y: scroll; }
            *, *:before, *:after { box-sizing: inherit; }
            body { margin:0; background: #fafafa; }
        </style>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"></script>
        <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-standalone-preset.js"></script>
        <script>
            window.onload = function() {
                const ui = SwaggerUIBundle({
                    url: '/api/v1/openapi.json',
                    dom_id: '#swagger-ui',
                    deepLinking: true,
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIStandalonePreset
                    ],
                    plugins: [
                        SwaggerUIBundle.plugins.DownloadUrl
                    ],
                    layout: "StandaloneLayout",
                    tryItOutEnabled: true,
                    supportedSubmitMethods: ['get', 'post', 'put', 'delete', 'patch'],
                    docExpansion: 'list',
                    jsonEditor: true,
                    defaultModelRendering: 'schema',
                    showRequestHeaders: true,
                    showCommonExtensions: true
                });
            };
        </script>
    </body>
    </html>
    """
    
    logger.debug("Serving Swagger UI interface")
    return swagger_ui_html, 200, {'Content-Type': 'text/html'}
