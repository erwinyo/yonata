import requests

from .printers import say_greeting

def get_google():
    response = requests.get('https://www.google.com')
    print(f"Status Code: {response.status_code}")

def main():
    get_google()
    say_greeting()

if __name__ == "__main__":
    main()