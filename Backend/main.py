from fastapi import FastAPI, status, Depends
import classes
from urllib.parse import urljoin
import model
from database import engine, get_db
from sqlalchemy.orm import Session
from typing import List
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup

model.Base.metadata.create_all(bind=engine)
app = FastAPI()

origins = [
    'http://localhost:3000'
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)


@app.get("/mensagens", response_model=List[classes.Mensagem], status_code=status.HTTP_200_OK)
async def buscar_valores(db: Session = Depends(get_db), skip: int = 0, limit: int=100):
    mensagens = db.query(model.Model_Mensagem).offset(skip).limit(limit).all()
    return mensagens


@app.get("/")
def read_root():
    return {"Hello": "lala"}

@app.post("/criar", status_code=status.HTTP_201_CREATED)
def criar_valores(nova_mensagem: classes.Mensagem, db: Session = Depends(get_db)):
    mensagem_criada = model.Model_Mensagem(**nova_mensagem.model_dump())
    db.add(mensagem_criada)
    db.commit()
    db.refresh(mensagem_criada)
    return {"Mensagem": mensagem_criada}


@app.get("/quadrado/{num}")
def square(num: int):
    return num ** 2

def web_scraping_and_save(db: Session):

    url = "https://ufu.br/"  

    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

     
        menu_items = soup.find_all('a', class_='nav-link')  


        for item in menu_items:
            menu_name = item.get_text(strip=True)

            menu_link = urljoin(url, item.get('href'))

         
            menu_item = model.Model_MenuNav(menuNav=menu_name, link=menu_link)

           
            db.add(menu_item)
        db.commit()
    else:
        print(f"Erro ao acessar a página: {response.status_code}")




@app.post("/scraping", status_code=status.HTTP_200_OK)
def realizar_scraping(db: Session = Depends(get_db)):
    web_scraping_and_save(db)
    return {"message": "Dados extraídos e salvos com sucesso!"}

