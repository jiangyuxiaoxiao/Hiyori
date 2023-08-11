if not exist .\venv\ (
    pip install virtualenv
    pip install -r requirements.txt
)
call venv\Scripts\activate
cd .\Hiyori
python hiyori.py
pause