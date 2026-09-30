from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from datetime import datetime
import httpx

from app.database import engine, Base, get_db
from app.models import CityQuery
from app.config import settings
from prometheus_fastapi_instrumentator import Instrumentator

# Создаем таблицы в БД при старте
Base.metadata.create_all(bind=engine)

# Инициализируем приложение. Swagger (А4) генерируется автоматически по адресу /docs
app = FastAPI(
    title="City Weather Planner API",
    description="Сервис для сохранения городов и получения актуальной погоды через внешнее API",
    version="1.0.0",
    docs_url="/docs"
)

# Подключаем экспорт метрик (для Prometheus из Блока Б)
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# Схемы валидации входящих данных
class CityCreate(BaseModel):
    city_name: str = Field(..., min_length=2, max_length=100, example="Moscow")
    latitude: float = Field(..., ge=-90, le=90, example=55.7558)
    longitude: float = Field(..., ge=-180, le=180, example=37.6173)

class CityResponse(CityCreate):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

# --- ЭНДПОИНТЫ API ---

@app.get("/health", tags=["Health"])
def health_check():
    """Проверка жизнеспособности сервиса (Smoke-test для Блока Б5)"""
    return {"status": "healthy"}

@app.post("/api/v1/cities", response_model=CityResponse, status_code=status.HTTP_201_CREATED, tags=["Cities"])
def create_city(city: CityCreate, db: Session = Depends(get_db)):
    """Метод 1 (Запись в БД): Сохранение города"""
    db_city = CityQuery(
        city_name=city.city_name,
        latitude=city.latitude,
        longitude=city.longitude
    )
    db.add(db_city)
    db.commit()
    db.refresh(db_city)
    return db_city

@app.get("/api/v1/cities", response_model=list[CityResponse], tags=["Cities"])
def get_cities(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Метод 2 (Чтение из БД): Получение сохраненных городов"""
    return db.query(CityQuery).offset(skip).limit(limit).all()

@app.get("/api/v1/weather", tags=["Weather"])
async def get_weather(latitude: float, longitude: float):
    """Метод 3 (Внешнее API): Запрос актуальной погоды с сервера Open-Meteo"""
    try:
        async with httpx.AsyncClient() as client:
            url = f"{settings.EXTERNAL_API_URL}?latitude={latitude}&longitude={longitude}&current=temperature_2m"
            response = await client.get(url, timeout=5.0)
            response.raise_for_status()
            data = response.json()
            
            temperature = data.get("current", {}).get("temperature_2m")
            return {
                "latitude": latitude,
                "longitude": longitude,
                "temperature_celsius": temperature
            }
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Ошибка внешнего сервиса погоды: {str(e)}")