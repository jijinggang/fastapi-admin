import sys  # noqa
sys.path.append("./")  # noqa

import os

import uvicorn
from fastapi import Depends, FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.templating import Jinja2Templates
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import pydantic_queryset_creator

from fastapi_admin.depends import get_model
from fastapi_admin.factory import app as admin_app
from fastapi_admin.schemas import BulkIn
from fastapi_admin.site import Site

db_url = "mysql://mysql:123456@127.0.0.1:3306/fastapi-admin"
TORTOISE_ORM = {
    "connections": {"default": db_url},
    "apps": {
        "models": {
            "models": ["examples.models", "fastapi_admin.models"],
            "default_connection": "default",
        }
    },
}

templates = Jinja2Templates(directory="examples/templates")


@admin_app.post("/rest/{resource}/bulk/test_bulk")
async def test_bulk(bulk_in: BulkIn, model=Depends(get_model)):
    qs = model.filter(pk__in=bulk_in.pk_list)
    pydantic = pydantic_queryset_creator(model)
    ret = await pydantic.from_queryset(qs)
    return ret.dict()


@admin_app.get("/home",)
async def home():
    return {"html": templates.get_template("home.html").render()}


def create_app():
    fast_app = FastAPI(debug=False)
    register_tortoise(fast_app, config=TORTOISE_ORM, generate_schemas=True)
    fast_app.mount("/admin", admin_app)

    fast_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from fastapi.staticfiles import StaticFiles
    fast_app.mount(
        "/", StaticFiles(directory="static", html=True), name="static")

    return fast_app


app = create_app()


@app.on_event("startup")
async def start_up():
    admin_app.init(
        admin_secret="test",
        permission=True,
        site=Site(
            name="FastAPI-Admin DEMO",
            login_footer="FASTAPI ADMIN - FastAPI Admin Dashboard",
            login_description="FastAPI Admin Dashboard",
            locale="en-US",
            locale_switcher=True,
            theme_switcher=True,
        ),
    )


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, debug=False,
                reload=False, lifespan="on")
