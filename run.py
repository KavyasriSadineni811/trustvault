
import webbrowser

from threading import Timer

from app import create_app


app = create_app()


def open_browser():
    webbrowser.open_new(
        "http://127.0.0.1:5000/"
    )


if __name__ == "__main__":

    # Automatically open TrustVault
    # in the default browser after Flask starts.
    Timer(
        1.5,
        open_browser
    ).start()

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
