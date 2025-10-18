from fastapi import FastAPI

app = FastAPI(title = "ecourt-scrapper")


@app.get("/")
def root():
    return {"message": "ecourt-scrapper is running!"}

@app.get("/api/health")
def health():
    return {"status": "ok"}




def main():
    print("Hello from ecourt-scrapper!")


if __name__ == "__main__":
    main()
