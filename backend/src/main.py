import os
import sys
from contextlib import asynccontextmanager

# Add the src directory to Python path to fix imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from responses import JSONResponse

from config import get_settings

from handlers import api_router

settings = get_settings()

app = FastAPI(
    default_response_class=JSONResponse,
    title="AI Research Assistant API",
    description="A sophisticated AI-powered research assistant with web search capabilities",
    debug=settings.mode != "production",
    docs_url="/swagger",
    swagger_ui_parameters={
        "docExpansion": "list",
        "persistAuthorization": True,
        "syntaxHighlight.theme": "obsidian",
        "filter": True,
        "custom_js": """
            window.addEventListener('load', function() {
                setTimeout(function() {
                    const infoContainer = document.querySelector('.info');
                    if (infoContainer) {
                        const infoDesc = infoContainer.querySelector('.info__desc');
                        if (infoDesc) {
                            const text = infoDesc.innerHTML;
                            const utcTimestampMatch = text.match(/Deployed: (.*)/);
                            
                            if (utcTimestampMatch && utcTimestampMatch[1]) {
                                const utcTimestamp = utcTimestampMatch[1].replace(' UTC', '');
                                const utcDate = new Date(utcTimestamp);
                                
                                if (!isNaN(utcDate)) {
                                    const localTimestamp = utcDate.toLocaleString();
                                    infoDesc.innerHTML = text.replace(
                                        utcTimestampMatch[1],
                                        localTimestamp
                                    );
                                }
                            }
                        }
                    }
                }, 500); // Small delay to ensure DOM is fully loaded
            });
        """
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    settings = get_settings()
    openapi_schema = get_openapi(
        title="AI Research Assistant API",
        summary="Sophisticated AI research assistant with web search and safety features",
        routes=app.routes,
        version="1.0.0",
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
