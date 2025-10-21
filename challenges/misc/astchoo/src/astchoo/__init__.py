from fastapi import FastAPI
from pydantic import BaseModel
import ast
from fastapi.responses import JSONResponse, FileResponse 
import typing
import contextlib
from io import StringIO
from pathlib import Path

app = FastAPI()

flag_path = Path("flag.txt")
if not flag_path.is_file():
    with flag_path.open("w+") as f:
        f.write("NNS{demo-flag}")


class ExecSchema(BaseModel):
    code: str

@app.get("/")
async def ui():
    return FileResponse("index.html")
@app.post("/")
def execute(schema: ExecSchema):
    try:
        parsed = ast.parse(schema.code)
    except Exception as e:
        return JSONResponse({"detail": str(e)}, status_code=400)

    validator = Validator()
    validator.visit(parsed)
    if not validator.valid:
        return JSONResponse({"detail": "denied by astchoo validator"}, status_code=400)

    out = StringIO()
    scope = {
        "print": print,
        "__builtins__": {}
    }
    with contextlib.redirect_stdout(out):
        try:
            exec(schema.code, scope, scope)
        except BaseException as e:
            return JSONResponse({"detail": str(e)}, status_code=400)

    
    out.seek(0)
    return {
        "output": out.read()
    }

class Validator(ast.NodeVisitor):
    def __init__(self):
        super().__init__()
        self.valid = True
        self.strict = False

    def generic_visit(self, node: ast.AST):
        allowed_node_types: list[typing.Type[ast.AST]] = [
            ast.Add,
            ast.Sub,
            ast.Mult,
            ast.Div,
            ast.Pow,
            ast.Mod,
            ast.FloorDiv,
            ast.Constant,
            ast.BinOp,
        ]
        normally_allowed_node_types: list[typing.Type[ast.AST]] = [
            ast.Expr,
            ast.Name,
            ast.Return,
            ast.Load,
            ast.Store,
            ast.Module,
            ast.FunctionDef,
            ast.Assign,
            ast.AnnAssign,
            ast.Call,
            ast.arguments
        ]
        if not self.strict:
            allowed_node_types.extend(normally_allowed_node_types)
        if type(node) not in allowed_node_types:
            self.valid = False

        super().generic_visit(node)

    def visit_Assign(self, node):
        old_strict = self.strict
        self.strict = True
        self.visit(node.value)
        self.strict = old_strict
    def visit_AnnAssign(self, node):
        old_strict = self.strict
        self.strict = True
        self.visit(node.value)
        self.strict = old_strict
