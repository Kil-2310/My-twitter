from fastapi import FastAPI

def create_app():

    app = FastAPI()

    @app.get('/')
    def index_page():
        return 'hello'

    return app
