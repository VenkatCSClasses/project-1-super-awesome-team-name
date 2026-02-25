from typer import Typer

app = Typer(no_args_is_help=True)

@app.callback()
def main():
    pass

@app.command()
def login(username: str):
    print(f"Logging in as {username}!")


if __name__ == "__main__":
    app()