from typer import Typer

app = Typer(no_args_is_help=True)

@app.command()
def hello(name: str):
    print(f"Hello {name}!")


if __name__ == "__main__":
    app()