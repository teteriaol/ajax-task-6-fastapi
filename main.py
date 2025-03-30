from controllers.salary_controller import SalaryController
from models.models import PositionCreate, PositionResponse, DependencyCreate, SalaryCalculationResponse
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn


app = FastAPI()
controller = SalaryController()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# gets

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/calculate/", response_model=SalaryCalculationResponse)
async def calculate_salaries():
    results = controller.calculate_salaries()
    return {"results": results}


@app.get("/positions/", response_model=list[PositionResponse])
async def get_positions():
    return controller.get_all_positions()

# posts

@app.post("/positions/", response_model=PositionResponse)
async def create_position(position: PositionCreate):
    return controller.add_new_position(position_name=position.name, base_salary=position.base_salary, bonus=position.bonus)



@app.post("/dependencies/", response_model=dict)
async def create_dependency(dependency: DependencyCreate):
        controller.create_dependency(from_position=dependency.from_position, from_level=dependency.from_level ,to_position=dependency.to_position, to_level=dependency.to_level,
                               formula_salary=dependency.formula_salary, formula_bonus=dependency.formula_bonus)
        return {"message": "Success"}

# other

@app.delete("/positions/{position_name}")
async def delete_position(position_name: str):
    controller.delete_position(position_name)
    return {"message": "Success"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
