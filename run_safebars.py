"""Run the SafeBARS prototype on a local development port."""

from app import app


if __name__ == "__main__":
    print("SafeBARS prototype: http://127.0.0.1:5050/safebars")
    app.run(debug=False, host="127.0.0.1", port=5050)

